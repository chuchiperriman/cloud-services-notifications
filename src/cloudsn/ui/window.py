# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
import gtk
import os
import shutil
import gettext
from cloudsn.core import config, provider, account, indicator, keyring
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
        self.pref_dialog = None
        self.config = config.SettingsController.get_instance()
        self.pm = provider.ProviderManager.get_instance()
        self.am = account.AccountManager.get_instance()
        self.im = indicator.IndicatorManager.get_instance()
        self.km = keyring.KeyringManager.get_instance()
        self.am.connect ("account-deleted", self.account_deleted_cb)

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
    
    def select_provider_combo (self, providers_combo, name):
        #Select the provider and disable item
        i=0
        for row in providers_combo.get_model():
            if row[1] == name:
                providers_combo.set_active (i)
                break
            i += 1

    def load_window(self):
        from cloudsn.core.controller import Controller
        
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
        self.play_button = self.builder.get_object("tool_play");
        
        #Populate accounts
        for acc in self.am.get_accounts():
            self.main_store.append([acc.get_icon(), acc.get_name(),
                self.__get_account_date(acc), acc.get_active()])
        
        #Populate providers
        for prov in self.pm.get_providers():
            self.providers_store.append([prov.get_icon(), prov.get_name()])

        #Update the last check date
        Controller.get_instance().connect ("account-checked", 
            self.__on_account_checked_cb)
        
        Controller.get_instance().connect ("account-check-error", 
            self.__on_account_check_error_cb)
        
        self.set_play_active (Controller.get_instance().get_active())
        
    def run(self):
        self.load_window()
        self.window.show()

    def set_play_active(self, active):
        self.play_button.set_active(active)
        if active:
            self.play_button.set_stock_id(gtk.STOCK_MEDIA_PAUSE)
            self.play_button.set_tooltip_text(
                _("Press to pause the checker daemon"))
        else:
            self.play_button.set_stock_id(gtk.STOCK_MEDIA_PLAY)
            self.play_button.set_tooltip_text(
                _("Press to start the checker daemon"))
    
    def preferences_action_activate_cb (self, widget, data=None):
        self.pref_dialog = self.builder.get_object("preferences_dialog")
        self.pref_dialog.set_transient_for(self.window)
        self.pref_dialog.set_destroy_with_parent (True)
        indicator_combo = self.builder.get_object("indicator_combo")
        indicators_store = self.builder.get_object("indicators_store");
        keyring_combo = self.builder.get_object("keyring_combo")
        keyring_store = self.builder.get_object("keyring_store");
        minutes=self.builder.get_object("minutes_spin")
        max_not_spin=self.builder.get_object("max_not_spin")
        startup_check = self.builder.get_object("startup_check")
        
        minutes.set_value (float(self.config.get_prefs()["minutes"]))
        max_not_spin.set_value (float(self.config.get_prefs()["max_notifications"]))
        if os.path.exists(config.get_startup_file_path()):
            startup_check.set_active(True)
        else:
            startup_check.set_active(False)
        #Populate indicator combo
        i=0
        indicator_name = self.config.get_prefs()["indicator"]
        indicators_store.clear()
        for indi in self.im.get_indicators():
            indicators_store.append([indi.get_name()])
            if indi.get_name() == indicator_name:
                indicator_combo.set_active(i)
            i+=1
        i=0
        keyring_id = self.config.get_prefs()["keyring"]
        keyring_store.clear()
        for k in self.km.get_managers():
            keyring_store.append([k.get_name()])
            if k.get_id() == keyring_id:
                keyring_combo.set_active(i)
            i+=1
        response = self.pref_dialog.run()
        self.pref_dialog.hide()
        self.config.set_pref ("minutes", minutes.get_value())
        self.config.set_pref ("max_notifications", max_not_spin.get_value())
        iiter = indicator_combo.get_active_iter()
        if iiter:
            self.config.set_pref ("indicator", indicators_store.get_value(iiter,0))
        iiter = keyring_combo.get_active_iter()
        #TODO Use the id, not the name
        #if iiter:
        #    self.config.set_pref ("keyring", keyring_store.get_value(iiter,0))
        
        #Check startup checkbox
        if startup_check.get_active():
            if not os.path.exists(config.get_startup_file_path()):
                if not os.path.exists(config.get_startup_file_dir()):
                    os.makedirs(config.get_startup_file_dir())
                shutil.copyfile(config.add_data_prefix("cloudsn.desktop"),
                    config.get_startup_file_path())
        else:
            if os.path.exists(config.get_startup_file_path()):
                os.remove (config.get_startup_file_path())
            
        self.config.save_prefs()
        
    def about_action_activate_cb (self, widget, data=None):
        about.show_about_dialog()

    def quit_action_activate_cb (self, widget, data=None):
        gtk.main_quit()

    def close_action_activate_cb (self, widget, data=None):
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

    def main_update_button_clicked_cb(self, widget, data=None):
        from cloudsn.core.controller import Controller
        acc, citer = self.get_main_account_selected()
        if acc:
            Controller.get_instance().update_account(acc)
    
    def tool_play_toggled_cb (self, widget, data=None):
        from cloudsn.core.controller import Controller
        self.set_play_active(widget.get_active())
        Controller.get_instance().set_active(widget.get_active())
    
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
    
    def active_cell_toggled_cb(self, cell, path, data=None):
        active = not self.main_store[path][3]
        self.main_store[path][3] = active
        account_name = self.main_store[path][1]
        acc = self.am.get_account(account_name)
        self.am.set_account_active(acc, active)
    
    def new_action_activate_cb(self, widget, data=None):
        self.new_dialog = self.builder.get_object("account_new_dialog")
        account_name_entry = self.builder.get_object("account_name_entry");
        self.provider_content = self.builder.get_object("provider_content")
        self.provider_content.account = None
        self.new_dialog.set_transient_for(self.window)
        self.new_dialog.set_destroy_with_parent (True)
        account_name_entry.set_text("")
        account_name_entry.set_sensitive (True)
        self.providers_combo.set_sensitive (True)
        self.providers_combo.set_active(-1)
        for c in self.provider_content.get_children():
            if c:
                self.provider_content.remove(c)
                c.destroy()
        end = False
        while not end:
            response = self.new_dialog.run()
            if response == 0:
                try:
                    if len(self.provider_content.get_children())==0:
                        raise Exception(_("You must select a provider and fill the data"))

                    acc_name = account_name_entry.get_text()
                    if acc_name == '':
                        raise Exception(_("You must fill the account name"))
                    
                    custom_widget = self.provider_content.get_children()[0]
                    citer = self.providers_combo.get_active_iter()
                    provider_name = self.providers_store.get_value (citer, 1)
                    provider = self.pm.get_provider(provider_name)
                    
                    acc = provider.set_account_data_from_widget(acc_name, custom_widget)
                    self.am.add_account(acc)
                    self.am.save_account(acc)
                    self.main_store.append([acc.get_icon(),
                            acc.get_name(),self.__get_account_date(acc),
                            acc.get_active()])
                    end = True
                except Exception, e:
                    logger.error ('Error adding a new account: ' + str(e))
                    md = gtk.MessageDialog(self.window,
                        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                        gtk.BUTTONS_CLOSE,
                        _('Error adding a new account: ') + str(e))
                    md.run()
                    md.destroy()
            else:
                end = True
            
        self.new_dialog.hide()
    
    def edit_action_activate_cb(self, widget, data=None):
        
        acc, citer = self.get_main_account_selected()
        
        if not acc:
            return
        
        self.new_dialog = self.builder.get_object("account_new_dialog")
        account_name_entry = self.builder.get_object("account_name_entry");
        account_name_entry.set_text(acc.get_name())
        #TODO the name cannot be modified by the moment
        account_name_entry.set_sensitive (False)
        self.provider_content = self.builder.get_object("provider_content")
        self.provider_content.account = acc
        self.new_dialog.set_transient_for(self.window)
        self.new_dialog.set_destroy_with_parent (True)
        
        #Select the provider and disable item
        providers_combo = self.builder.get_object("providers_combo")
        providers_combo.set_active(-1)
        self.select_provider_combo (providers_combo, acc.get_provider().get_name())
        
        providers_combo.set_sensitive (False)
        
        end = False
        while not end:
            response = self.new_dialog.run()
            if response == 0:
                try:
                    acc_name = account_name_entry.get_text()
                    if acc_name == '':
                        raise Exception(_("You must fill the account name"))
                    
                    custom_widget = self.provider_content.get_children()[0]
                    
                    acc = acc.get_provider().set_account_data_from_widget(acc_name, custom_widget, acc)
                    self.am.save_account(acc)
                    end = True
                except Exception, e:
                    logger.error ('Error editing an account: ' + str(e))
                    md = gtk.MessageDialog(self.window,
                        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                        gtk.BUTTONS_CLOSE,
                        _('Error editing an account: ') + str(e))
                    md.run()
                    md.destroy()
            else:
                end = True
            
        self.new_dialog.hide()
    
    def update_all_action_activate_cb (self, widget, data=None):
        from cloudsn.core.controller import Controller
        Controller.get_instance().update_accounts()
        
    def providers_combo_changed_cb(self, widget, data=None):
        ch = self.provider_content.get_children()
        for c in ch:
            self.provider_content.remove(c)
            c.destroy()
        
        citer = self.providers_combo.get_active_iter()
        if not citer:
            return
        provider_name = self.providers_store.get_value (citer, 1)
        provider = self.pm.get_provider(provider_name)

        box =  provider.get_account_data_widget(self.provider_content.account)
        self.provider_content.add(box)
        box.show_all()

    def __on_account_checked_cb(self, widget, acc):
        for row in self.main_store:
            if row[1] == acc.get_name():
                row[0] = acc.get_icon()
                row[2] = self.__get_account_date(acc)

    def __on_account_check_error_cb(self, widget, acc):
        for row in self.main_store:
            if row[1] == acc.get_name():
                row[0] = acc.get_icon()
                row[2] = self.__get_account_date(acc)

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


