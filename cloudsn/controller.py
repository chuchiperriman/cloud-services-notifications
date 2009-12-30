import provider
import account
import indicate
from time import time
import gtk
import gobject
import config

class Controller:

    timeout_id = -1
    interval = 60
    
    def __init__(self):
        self.config = config.GetSettingsController()
        self.config.connect("value-changed", self._settings_changed)
        self.prov_manager = provider.GetProviderManager()
        self.am = account.GetAccountManager()
        self.am.connect("account-added", self._account_added_cb)
        self.am.connect("account-deleted", self._account_deleted_cb)

    def _account_added_cb(self, am, account):
        self.create_indicator(account)
        print 'account added: ', account.get_name()

    def _account_deleted_cb(self, am, account):
        account.indicator = None
        print 'account deleted: ', account.get_name()
    
    def _settings_changed(self, config, section, key, value):
        if section == "preferences" and key == "minutes":
            self._update_interval()

    def _update_interval(self):
        old = self.interval
        self.interval = int(float(self.config.get_prefs()["minutes"]) * 60)
        if self.timeout_id < 0:
            self.timeout_id = gobject.timeout_add_seconds(self.interval, self.update_accounts, None)
        elif self.interval != old:
            gobject.source_remove(self.timeout_id)
            self.timeout_id = gobject.timeout_add_seconds(self.interval, self.update_accounts, None)
        
    def on_server_display_cb(self, server):
        import preferences
        prefs = preferences.GetPreferences()
        prefs.quit_on_destroy = True
        prefs.run()
        
    def init_indicator_server(self):
        self.server = indicate.indicate_server_ref_default()
        self.server.set_type("message.im")
        self.server.connect("server-display", self.on_server_display_cb)
        self.server.set_desktop_file(config.get_data_dir() + "/cloudsn.desktop")
        self.server.show()

    def on_indicator_display_cb(self, indicator):
        indicator.account.activate ()

    def create_indicator(self, account):
        indicator = indicate.Indicator()
        indicator.set_property("name", account.get_name())
        indicator.set_property_time("time", time())
        indicator.set_property_int("count", account.get_unread())
        if account.get_provider().get_icon() is not None:
            indicator.set_property_icon("icon", account.get_provider().get_icon())
        indicator.show()
        indicator.connect("user-display", self.on_indicator_display_cb)
        account.indicator = indicator
        indicator.account = account
        
    def notify (self, title, message):
        try:
            import pynotify
            if pynotify.init("Cloud Services Notifications"):
                n = pynotify.Notification(title, message)
                n.set_urgency(pynotify.URGENCY_LOW)
                n.show()
            else:
                print "there was a problem initializing the pynotify module"
        except:
            print "you don't seem to have pynotify installed"

    def update_accounts(self, other):
        for acc in self.am.get_accounts():
            try:
                acc.update()
                acc.indicator.set_property_int("count", acc.get_unread())
                if acc.get_provider().has_notifications() and acc.get_new_unread() > 0:
                    self.notify(acc.get_name(), "New messages: " + str(acc.get_new_unread()))
            except Exception as e:
                print "Error trying to update the account " , acc.get_name() , ": " , e
                
        #account.indicator.set_property('draw-attention', 'true');
        return True

    def _start_idle(self):
        self.update_accounts(None)
        self._update_interval()
        return False
        
    def start(self):
        self.init_indicator_server()
        for provider in self.prov_manager.get_providers():
            provider.register_accounts()
            
        while gtk.events_pending():
            gtk.main_iteration(False)
            
        gobject.idle_add(self._start_idle)
        gtk.main()

_controller = None

def GetController():
    global _controller
    if _controller is None:
        _controller = Controller()
    return _controller

