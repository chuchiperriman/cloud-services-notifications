from cloudsn.core.provider import Provider, ProviderManager
from cloudsn.core import account, config, networkmanager, notification, utils
from cloudsn.ui import preferences
from cloudsn import logger
from time import time
import gtk
import gobject
import gettext

class Controller (gobject.GObject):

    __default = None

    __gtype_name__ = "Controller"

    __gsignals__ = { "account-checked" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}

    timeout_id = -1
    interval = 60
    
    def __init__(self):
        if Controller.__default:
           raise Controller.__default

        #Prevent various instances
        import os, fcntl, sys, tempfile, getpass
        self.lockfile = os.path.normpath(tempfile.gettempdir() + '/cloudsn-'+getpass.getuser()+'.lock')
        self.fp = open(self.lockfile, 'w')
        try:
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            message = _("Another instance is already running, quitting.")
            logger.warn (message)
            print message
            sys.exit(-1)

        gobject.GObject.__init__(self)
        self.started = False
        self.config = config.SettingsController.get_instance()
        self.config.connect("value-changed", self._settings_changed)
        self.prov_manager = ProviderManager.get_instance()
        self.am = account.AccountManager.get_instance()
        self.am.connect("account-added", self._account_added_cb)
        self.am.connect("account-deleted", self._account_deleted_cb)
        self.am.load_accounts()

    @staticmethod
    def get_instance():
        if not Controller.__default:
            Controller.__default = Controller()
        return Controller.__default

    def _account_added_cb(self, am, acc):
        self.create_indicator(acc)

        while gtk.events_pending():
            gtk.main_iteration(False)
            
        if self.started:
            self.update_account(acc)

    def _account_deleted_cb(self, am, acc):
        acc.indicator = None
    
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
        prefs = preferences.Preferences.get_instance()
        prefs.run()
        
    def init_indicator_server(self):
        try:
            import indicate
            self.server = indicate.indicate_server_ref_default()
            self.server.set_type("message.im")
            self.server.connect("server-display", self.on_server_display_cb)
            self.server.set_desktop_file(config.add_apps_prefix("cloudsn.desktop"))
            self.server.show()
            logger.debug("Indicator server created")
        except Exception, e:
            logger.exception("Error loading the indicate server: %s", e)
            
    def on_indicator_display_cb(self, indicator):
        indicator.account.activate ()

    def on_nm_state_changed (self):
        if self.nm.state == networkmanager.STATE_CONNECTED:
            logger.debug("Network connected")
            #Force update
            self.update_accounts()
        else:
            logger.debug("Network disconnected")
    
    def create_indicator(self, acc):
        try:
            import indicate
            indicator = indicate.Indicator()
            indicator.set_property("name", acc.get_name())
            indicator.set_property_time("time", time())
            indicator.set_property_int("count", acc.get_total_unread())
            if acc.get_provider().get_icon() is not None:
                indicator.set_property_icon("icon", acc.get_provider().get_icon())
            indicator.show()
            indicator.connect("user-display", self.on_indicator_display_cb)
            acc.indicator = indicator
            indicator.account = acc
        except Exception, e:
            logger.exception("Error creating the indicator: %s",e)
        
    def update_account(self, acc):
        """acc=None will check all accounts"""
        if self.nm.offline():
            logger.warn ("The network is not connected, the account cannot be updated")
            return
        #TODO Check if the updater is running
        self.__real_update_account(acc)

    def __real_update_account(self, paramacc):
        
        logger.debug("Starting checker")
        for acc in self.am.get_accounts():
            if self.nm.state != networkmanager.STATE_CONNECTED:
                logger.debug("The network is not connected, the accounts will not be updated")
                return
                
            if acc.get_active() and (paramacc is None or paramacc == acc):
                try:
                    logger.debug('Updating account: ' + acc.get_name())
                    self.am.update_account(acc)
                    acc.error_notified = False
                    if hasattr(acc, "indicator"):
                        acc.indicator.set_property_int("count", acc.get_total_unread())
                    if acc.get_provider().has_notifications():
                        nots = acc.get_new_unread_notifications()
                        message = None
                        if len(nots) > 0:
                            message = _("New messages: ") + str(len(nots))
                            
                        if len(nots) <= 3:
                            for n in nots:
                                message += "\n" + n.message

                        if message:
                            notification.notify(acc.get_name(), 
                                message,
                                acc.get_provider().get_icon())
                            #account.indicator.set_property('draw-attention', 'true');
                    self.emit("account-checked", acc)
                except notification.NotificationError, ne:
                    logger.exception("Error trying to notify with libnotify: %s", e)
                except Exception, e:
                    logger.exception("Error trying to update the account %s: %s", acc.get_name(), e)
                    if not acc.error_notified:
                        notification.notify (_("Error checking account %s") % (acc.get_name()),
                            str(e),
                            utils.get_error_pixbuf())
                        acc.error_notified = True

        logger.debug("Ending checker")
        
    def update_accounts(self, data=None):
        self.update_account(None)
        #For the timeout_add_seconds
        return True

    def _start_idle(self):
        try:
            self.init_indicator_server()
            self.nm = networkmanager.NetworkManager()
            self.nm.set_statechange_callback(self.on_nm_state_changed)
            self.update_accounts()
            self._update_interval()
            self.started = True
        except Exception, e:
            logger.exception ("Error starting the application: %s", e)
            try:
                notification.notify(_("Application Error"), 
                    _("Error starting the application: %s") % (str(e)),
                    utils.get_error_pixbuf())
            except Exception, e:
                logger.exception ("Error notifying the error: %s", e)
            
        return False

    def signint(self, signl, frme):
        gobject.source_remove(self.timeout_id)
        gtk.main_quit()
        return 0

    def start(self):
        import signal
        signal.signal( signal.SIGINT, self.signint )
        gobject.idle_add(self._start_idle)
        try:
            gtk.main()
        except KeyboardInterrupt:
            logger.info ('KeyboardInterrupt the main loop')

