import gtk
import config
import provider
import account

STOP_RESPONSE = 1

class Preferences:

    def __init__ (self):
        self.window = None
        self.dialog_only = False
        self.config = config.GetSettingsController()
        self.pm = provider.GetProviderManager()
        self.am = account.GetAccountManager()

    def on_close_button_clicked (self, widget, data=None):
        self.window.response(True)

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
                    self.store.append([account.get_provider().get_icon(), account.get_name()])

    def on_account_edit_button_clicked(self, widget, data=None):
        selection = self.account_tree.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            citer = self.store.get_iter(path)
            account_name = self.store.get_value(citer, 1)
            acc = self.am.get_account(account_name)
            provider = acc.get_provider()
            if provider.edit_account_dialog(acc):
                self.am.edit_account(acc)
        
    def on_account_del_button_clicked (self, widget, data=None):
        selection = self.account_tree.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            citer = self.store.get_iter(path)
            account_name = self.store.get_value(citer, 1)
            acc = self.am.get_account(account_name)
            self.am.del_account(acc, True)
            self.store.remove(citer)

    def on_stop_button_clicked (self, widget, data=None):
        self.window.response(STOP_RESPONSE)
    
    def load_window(self):
        builder=gtk.Builder()
        builder.set_translation_domain("cloudsn")
        builder.add_from_file(config.get_data_dir() + "/preferences.ui")
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
        for prov in self.pm.get_providers():
            self.providers_store.append([prov.get_icon(), prov.get_name()])
        for acc in self.am.get_accounts():
            self.store.append([acc.get_provider().get_icon(), acc.get_name()])

        self.providers_combo.set_active(0)
        self.minutes.set_value (float(self.config.get_prefs()["minutes"]))
        
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
        

_preferences = None

def GetPreferences ():
    global _preferences
    if _preferences is None:
        _preferences = Preferences()
    return _preferences

def main ():
    for prov in provider.GetProviderManager().get_providers():
        prov.register_accounts()
    prefs = GetPreferences()
    prefs.dialog_only = True
    prefs.run()

if __name__ == "__main__":
    main()


