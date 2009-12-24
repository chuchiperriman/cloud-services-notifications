import gtk
import config

class Preferences:

    def __init__ (self):
        builder=gtk.Builder()
        builder.set_translation_domain("cloudsn")
        builder.add_from_file(config.get_data_dir() + "/preferences.ui")
        #builder.connect_signal(self)
        self.ventana=builder.get_object("dialog")

    def show(self):
        self.ventana.show()

_preferences = None

def GetPreferences ():
    global _preferences
    if _preferences is None:
        _preferences = Preferences()
    return _preferences

def main ():
    prefs = GetPreferences()
    prefs.show()

    gtk.main()

if __name__ == "__main__":
    main()


