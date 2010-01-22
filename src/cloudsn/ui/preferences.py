import gtk
import os
import shutil
from cloudsn.core import config, provider, account

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
                account = provider.create_account_dialog(account_name)
                if account is not None:
                    self.am.add_account(account, True)
                    self.store.append([account.get_provider().get_icon(), account.get_name(),''])

    def on_account_edit_button_clicked(self, widget, data=None):
        acc, citer = self.get_selected_account()
        provider = acc.get_provider()
        if provider.edit_account_dialog(acc):
            self.am.edit_account(acc)
        
    def on_account_del_button_clicked (self, widget, data=None):
        acc, citer = self.get_selected_account()
        self.am.del_account(acc, True)
        self.store.remove(citer)

    def on_stop_button_clicked (self, widget, data=None):
        self.window.response(STOP_RESPONSE)

    def on_update_button_clicked(self, widget, data=None):
        from cloudsn.core.controller import Controller

        selection = self.account_tree.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            citer = self.store.get_iter(path)
            account_name = self.store.get_value(citer, 1)
            acc = self.am.get_account(account_name)

        Controller.get_instance().update_account(acc)

    def on_startup_check_toggled(self, widget, data=None):
        if widget.get_active():
            if not os.path.exists(config.get_startup_file_path()):
                shutil.copyfile(config.add_data_prefix("cloudsn.desktop"),config.get_startup_file_path())
        else:
            os.remove (config.get_startup_file_path())

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
                row[2] = self.__get_account_date(acc)
    
    def load_window(self):
        from cloudsn.core.controller import Controller
        builder=gtk.Builder()
        builder.set_translation_domain("cloudsn")
        builder.add_from_file(config.add_data_prefix("preferences.ui"))
        builder.connect_signals(self)
        self.window=builder.get_object("dialog")
        self.minutes=builder.get_object("minutes_spin")
        #tests
        self.store = builder.get_object("account_store");
        self.account_tree = builder.get_object("account_treeview");
        self.dialog_new = builder.get_object("account_new_dialog");
        self.providers_combo = builder.get_object("providers_combo");
        self.providers_store = builder.get_object("providers_store");
        self.account_name_entry = builder.get_object("account_name_entry");
        self.startup_check = builder.get_object("startup_check")
        for prov in self.pm.get_providers():
            self.providers_store.append([prov.get_icon(), prov.get_name()])
        for acc in self.am.get_accounts():
            self.store.append([acc.get_provider().get_icon(), acc.get_name(), self.__get_account_date(acc)])

        self.providers_combo.set_active(0)
        self.minutes.set_value (float(self.config.get_prefs()["minutes"]))

        self.window.set_icon(config.get_cloudsn_icon())
        self.dialog_new.set_icon(config.get_cloudsn_icon())

        if os.path.exists(config.get_startup_file_path()):
            self.startup_check.set_active(True)
        else:
            self.startup_check.set_active(False)
        #Update the last check date
        Controller.get_instance().connect ("account-checked", self.__on_account_checked_cb)
        
    def run(self):
        if self.window is None:
            self.load_window()

        result = self.window.run()
        self.config.set_pref ("minutes", self.minutes.get_value())
        self.config.save_prefs()
        self.window.destroy()
        self.window = None
        if self.dialog_only == False and result == STOP_RESPONSE:
            gtk.main_quit()
        return result

def main ():
    for prov in provider.ProviderManager.get_instance().get_providers():
        prov.register_accounts()
    prefs = Preferences.get_instance()
    prefs.dialog_only = True
    prefs.run()

if __name__ == "__main__":
    main()


