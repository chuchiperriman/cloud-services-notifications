import gtk
import config

class Preferences:

    window = None
    quit_on_destroy = False
    
    def __init__ (self):
        pass
        
    def on_close_button_clicked (self, widget, data=None):
        self.window.response(True)
        
    def run(self):
        if self.window is None:
            builder=gtk.Builder()
            builder.set_translation_domain("cloudsn")
            builder.add_from_file(config.get_data_dir() + "/preferences.ui")
            builder.connect_signals(self)
            self.window=builder.get_object("dialog")
            #tests
            store = builder.get_object("account_store");
            icon = gtk.gdk.pixbuf_new_from_file(config.get_data_dir() + '/gmail.png')
            store.append(["uno"])
            store.append(["dos"])

        result = self.window.run()
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


