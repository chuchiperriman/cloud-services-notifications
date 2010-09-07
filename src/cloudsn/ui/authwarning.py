import gtk
import gettext
from cloudsn import logger
from ..core.config import SettingsController
from ..core.utils import get_boolean
from ..const import *

AUTH_DONT_ASK_KEY = "auth_dont_ask"

def check_auth_configuration():
    try:
        import gnomekeyring as gk
    except Exception:
        logger.debug("Gnome keyring is not available")
        return

    conf = SettingsController.get_instance()
    prefs = conf.get_prefs()
    if AUTH_DONT_ASK_KEY in prefs and get_boolean(prefs[AUTH_DONT_ASK_KEY]) == True:
        return

    label = gtk.Label()
    label.set_markup(_("""<b>Security warning</b>

You have gnome-keyring installed but your are using plain text encryption
to store your passwords. You can select the encryption method
in the preferences dialog.

"""))
    dialog = gtk.Dialog(APP_LONG_NAME,
                       None,
                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                       (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    dialog.vbox.pack_start(label)
    checkbox = gtk.CheckButton(_("Don't ask me again"))
    checkbox.show()
    dialog.vbox.pack_end(checkbox)
    label.show()
    response = dialog.run()
    dialog.destroy()
    if checkbox.get_active():
        conf.set_pref (AUTH_DONT_ASK_KEY, True)
        conf.save_prefs()

