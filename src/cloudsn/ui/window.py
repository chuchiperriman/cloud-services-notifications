import gtk
import os
import shutil
import gettext
from cloudsn.core import config, provider, account, indicator
from cloudsn import logger
from cloudsn.ui import about, utils

STOP_RESPONSE = 1

class MainWindow:

    __default = None

    def __init__ (self):
        if MainWindow.__default:
            raise MainWindow.__default
        self.builder = None
        self.window = None
        self.dialog_only = False
        self.config = config.SettingsController.get_instance()
        self.pm = provider.ProviderManager.get_instance()
        self.am = account.AccountManager.get_instance()
        self.im = indicator.IndicatorManager.get_instance()
        self.am.connect ("account-deleted", 
            self.account_deleted_cb)

    @staticmethod
    def get_instance():
        if not MainWindow.__default:
            MainWindow.__default = MainWindow()
        return MainWindow.__default

    def get_main_account_selected (self):
        selection = self.main_account_tree.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            citer = self.main_store.get_iter(path)
            account_name = self.main_store.get_value(citer, 1)
            acc = self.am.get_account(account_name)
            return acc, citer
        
        return None, None
    
    def __get_account_date(self, acc):
        last_update = ''
        dt = acc.get_last_update()
        if dt:
            last_update = dt.strftime("%Y-%m-%d %H:%M:%S")

        return last_update

    def load_window(self):
        self.builder=gtk.Builder()
        self.builder.set_translation_domain("cloudsn")
        self.builder.add_from_file(config.add_data_prefix("preferences.ui"))
        self.builder.connect_signals(self)
        self.window=self.builder.get_object("main_window")
        self.window.connect ("delete-event", self.window_delete_event_cb)
        self.window.set_icon(config.get_cloudsn_icon())
        self.main_account_tree = self.builder.get_object("main_account_tree");
        self.main_store = self.builder.get_object("account_store");
        self.providers_combo = self.builder.get_object("providers_combo");
        self.providers_store = self.builder.get_object("providers_store");
        
        #Populate accounts
        for acc in self.am.get_accounts():
            self.main_store.append([acc.get_icon(), acc.get_name(),
                self.__get_account_date(acc), acc.get_active()])
        
        #Populate providers
        for prov in self.pm.get_providers():
            print "prov",prov.get_name()
            self.providers_store.append([prov.get_icon(), prov.get_name()])
        """
        self.minutes=builder.get_object("minutes_spin")
        self.max_not_spin=builder.get_object("max_not_spin")
        #tests
        self.store = builder.get_object("account_store");
        self.account_tree = builder.get_object("account_treeview");
        self.dialog_new = builder.get_object("account_new_dialog");
        
        self.account_name_entry = builder.get_object("account_name_entry");
        self.startup_check = builder.get_object("startup_check")
        self.indicator_combo = builder.get_object("indicator_combo")
        self.indicators_store = builder.get_object("indicators_store");
        
        for acc in self.am.get_accounts():
            self.store.append([acc.get_icon(), acc.get_name(),
                self.__get_account_date(acc), acc.get_active()])

        self.minutes.set_value (float(self.config.get_prefs()["minutes"]))
        self.max_not_spin.set_value (float(self.config.get_prefs()["max_notifications"]))

        self.window.set_icon(config.get_cloudsn_icon())
        self.dialog_new.set_icon(config.get_cloudsn_icon())

        if os.path.exists(config.get_startup_file_path()):
            self.startup_check.set_active(True)
        else:
            self.startup_check.set_active(False)
        #Populate indicator combo
        i=0
        indicator_name = self.config.get_prefs()["indicator"]
        for indi in self.im.get_indicators():
            self.indicators_store.append([indi.get_name()])
            if indi.get_name() == indicator_name:
                self.indicator_combo.set_active(i)
            i+=1

        #Update the last check date
        Controller.get_instance().connect ("account-checked", 
            self.__on_account_checked_cb)
        
        Controller.get_instance().connect ("account-check-error", 
            self.__on_account_check_error_cb)
        """
    def run(self):
        if self.window is None:
            self.load_window()

        self.window.show()
        """
        self.config.set_pref ("minutes", self.minutes.get_value())
        self.config.set_pref ("max_notifications", self.max_not_spin.get_value())
        iiter = self.indicator_combo.get_active_iter()
        if iiter:
            self.config.set_pref ("indicator", self.indicators_store.get_value(iiter,0))
        self.config.save_prefs()
        self.window.destroy()
        self.window = None
        if self.dialog_only == False and result == STOP_RESPONSE:
            gtk.main_quit()
        return result
        """

    def preferences_action_activate_cb (self, widget, data=None):
        print 'aaaa'

    def about_action_activate_cb (self, widget, data=None):
        about.show_about_dialog()

    def quit_action_activate_cb (self, widget, data=None):
        if self.dialog_only:
            gtk.main_quit()
        else:
            self.window.hide()

    def main_delete_button_clicked_cb(self, widget, data=None):
        acc, citer = self.get_main_account_selected()
        if not acc:
            return
            
        msg = (_('Are you sure you want to delete the account %s?')) % (acc.get_name());
        
        dia = gtk.MessageDialog(self.window,
                  gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                  gtk.MESSAGE_QUESTION,
                  gtk.BUTTONS_YES_NO,
                  msg)
        dia.show_all()
        if dia.run() == gtk.RESPONSE_YES:
            self.am.del_account(acc, True)
        dia.hide()

    def account_deleted_cb(self, widget, acc):
        for i in range(len(self.main_store)):
            if self.main_store[i][1] == acc.get_name():
                del self.main_store[i]
                break

    def window_delete_event_cb (self, widget, event, data=None):
        if self.dialog_only:
            gtk.main_quit()
        else:
            self.window.hide()
    
    def new_action_activate_cb(self, widget, data=None):
        self.new_dialog = self.builder.get_object("account_new_dialog")
        self.provider_content = self.builder.get_object("provider_content")
        self.new_dialog.set_transient_for(self.window)
        self.new_dialog.set_destroy_with_parent (True)
        response = self.new_dialog.run()
        if response == 0:
            print self.provider_content.get_children()[0]
        self.new_dialog.hide()
        
    def providers_combo_changed_cb(self, widget, data=None):
        print 'changed'
        ch = self.provider_content.get_children()
        for c in ch:
            self.provider_content.remove(c)
            c.destroy()
            
        box = utils.create_provider_widget ([{"label": "User:", "type" : "str"},
                {"label": "Password:", "type" : "pwd"}])
        #box.set_parent_window (self.new_dialog)
        self.provider_content.add(box)
        box.show_all()

def main ():
    import cloudsn.cloudsn
    import cloudsn.core.controller
    cloudsn.cloudsn.setup_locale_and_gettext()
    #account.AccountManager.get_instance().load_accounts()
    cloudsn.core.controller.Controller.get_instance()
    win = MainWindow.get_instance()
    win.dialog_only = True
    win.run()
    gtk.main()

if __name__ == "__main__":
    main()


