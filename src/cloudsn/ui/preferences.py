import gtk
import os
import shutil
from cloudsn.core import config, provider, account, indicator
from cloudsn import logger

STOP_RESPONSE = 1

class Preferences:

    __default = None

    def __init__ (self):
        if Preferences.__default:
           raise Preferences.__default
        self.window = None
        self.dialog_only = False
        self.config = config.SettingsController.get_instance()
        self.pm = provider.ProviderManager.get_instance()
        self.am = account.AccountManager.get_instance()
        self.im = indicator.IndicatorManager.get_instance()

    @staticmethod
    def get_instance():
        if not Preferences.__default:
            Preferences.__default = Preferences()
        return Preferences.__default

    def get_selected_account (self):
        selection = self.account_tree.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            citer = self.store.get_iter(path)
            account_name = self.store.get_value(citer, 1)
            acc = self.am.get_account(account_name)
            return acc, citer

    def on_close_button_clicked (self, widget, data=None):
        self.window.response(-1)

    def on_account_add_button_clicked (self, widget, data=None):
        response = self.dialog_new.run()
        self.dialog_new.hide()
        if response == 0:
            citer = self.providers_combo.get_active_iter()
            provider_name = self.providers_store.get_value (citer, 1)
            provider = self.pm.get_provider(provider_name)
            account_name = self.account_name_entry.get_text()
            if account_name != "":
                try:
                    self.am.validate_account(account_name)
                    account = provider.create_account_dialog(account_name, self.window)
                    if account is not None:
                        self.am.add_account(account)
                        self.am.save_account(account)
                        self.store.append([account.get_icon(),
                                account.get_name(),self.__get_account_date(account),
                                account.get_active()])
                except Exception, e:
                    logger.error ('Error adding a new account: ' + str(e))
                    md = gtk.MessageDialog(self.window,
                        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                        gtk.BUTTONS_CLOSE,
                        'Error adding a new account: ' + str(e))
                    md.run()
                    md.destroy()


    def on_account_edit_button_clicked(self, widget, data=None):
        acc, citer = self.get_selected_account()
        provider = acc.get_provider()
        if provider.edit_account_dialog(acc,self.window):
            self.am.save_account(acc)
        
    def on_account_del_button_clicked (self, widget, data=None):
        acc, citer = self.get_selected_account()
        self.am.del_account(acc, True)
        self.store.remove(citer)

    def on_stop_button_clicked (self, widget, data=None):
        self.window.response(STOP_RESPONSE)

    def on_update_button_clicked(self, widget, data=None):
        from cloudsn.core.controller import Controller
        acc = None
        selection = self.account_tree.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            citer = self.store.get_iter(path)
            account_name = self.store.get_value(citer, 1)
            acc = self.am.get_account(account_name)

        if acc:
            Controller.get_instance().update_account(acc)

    def on_startup_check_toggled(self, widget, data=None):
        if widget.get_active():
            if not os.path.exists(config.get_startup_file_path()):
                if not os.path.exists(config.get_startup_file_dir()):
                    os.makedirs(config.get_startup_file_dir())
                shutil.copyfile(config.add_data_prefix("cloudsn.desktop"),
                    config.get_startup_file_path())
        else:
            os.remove (config.get_startup_file_path())

    def on_active_cell_toglled (self, cell, path, data=None):
        active = not self.store[path][3]
        self.store[path][3] = active
        account_name = self.store[path][1]
        acc = self.am.get_account(account_name)
        self.am.set_account_active(acc, active)

    def on_update_all_button_clicked(self, widget, data=None):
        from cloudsn.core.controller import Controller
        Controller.get_instance().update_accounts()

    def __get_account_date(self, acc):
        last_update = ''
        dt = acc.get_last_update()
        if dt:
            last_update = dt.strftime("%Y-%m-%d %H:%M:%S")

        return last_update

    def __on_account_checked_cb(self, widget, acc):
        for row in self.store:
            if row[1] == acc.get_name():
                row[0] = acc.get_icon()
                row[2] = self.__get_account_date(acc)
    
    def __on_account_check_error_cb(self, widget, acc):
        for row in self.store:
            if row[1] == acc.get_name():
                row[0] = acc.get_icon()
                row[2] = self.__get_account_date(acc)
    
    def load_window(self):
        from cloudsn.core.controller import Controller
        builder=gtk.Builder()
        builder.set_translation_domain("cloudsn")
        builder.add_from_file(config.add_data_prefix("preferences.ui"))
        builder.connect_signals(self)
        self.window=builder.get_object("dialog")
        self.minutes=builder.get_object("minutes_spin")
        self.max_not_spin=builder.get_object("max_not_spin")
        #tests
        self.store = builder.get_object("account_store");
        self.account_tree = builder.get_object("account_treeview");
        self.dialog_new = builder.get_object("account_new_dialog");
        self.providers_combo = builder.get_object("providers_combo");
        self.providers_store = builder.get_object("providers_store");
        self.account_name_entry = builder.get_object("account_name_entry");
        self.startup_check = builder.get_object("startup_check")
        self.indicator_combo = builder.get_object("indicator_combo")
        self.indicators_store = builder.get_object("indicators_store");
        for prov in self.pm.get_providers():
            self.providers_store.append([prov.get_icon(), prov.get_name()])
        for acc in self.am.get_accounts():
            self.store.append([acc.get_icon(), acc.get_name(),
                self.__get_account_date(acc), acc.get_active()])

        self.providers_combo.set_active(0)
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
        
    def run(self):
        if self.window is None:
            self.load_window()

        result = self.window.run()
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

def main ():
    import cloudsn.cloudsn
    import cloudsn.core.controller
    cloudsn.cloudsn.setup_locale_and_gettext()
    #account.AccountManager.get_instance().load_accounts()
    cloudsn.core.controller.Controller.get_instance()
    prefs = Preferences.get_instance()
    prefs.dialog_only = True
    prefs.run()

if __name__ == "__main__":
    main()


