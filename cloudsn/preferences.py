import gtk
import config

class Preferences:

    window = None
    quit_on_destroy = False
    config = None
    
    def __init__ (self):
        self.config = config.GetSettingsController()
        pass
        
    def on_close_button_clicked (self, widget, data=None):
        self.window.response(True)

    def load_window(self):
        builder=gtk.Builder()
        builder.set_translation_domain("cloudsn")
        builder.add_from_file(config.get_data_dir() + "/preferences.ui")
        builder.connect_signals(self)
        self.window=builder.get_object("dialog")
        self.minutes=builder.get_object("minutes_spin")
        #tests
        store = builder.get_object("account_store");
        icon = gtk.gdk.pixbuf_new_from_file(config.get_data_dir() + '/gmail.png')
        store.append([icon, "uno"])
        store.append([icon, "dos"])
        
        self.minutes.set_value (float(self.config.get_prefs()["minutes"]))
        
    def run(self):
        if self.window is None:
            self.load_window()

        result = self.window.run()
        self.config.set_pref ("minutes", self.minutes.get_value())
        self.config.save_prefs()
        self.window.destroy()
        self.window = None
        

_preferences = None

def GetPreferences ():
    global _preferences
    if _preferences is None:
        _preferences = Preferences()
    return _preferences

def main ():
    prefs = GetPreferences()
    prefs.quit_on_destroy = True
    prefs.run()

if __name__ == "__main__":
    main()


