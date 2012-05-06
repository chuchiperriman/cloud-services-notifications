from gi.repository import Gtk
import gettext
from cloudsn import logger
from cloudsn.core.config import SettingsController, get_cloudsn_icon
from cloudsn.core.utils import get_boolean
from cloudsn.const import *
from cloudsn.core.keyring import get_keyring

AUTH_DONT_ASK_KEY = "auth_dont_ask"

def check_auth_configuration():
    try:
        import gnomekeyring as gk
        from ..core.keyrings import gkeyring
    except Exception:
        logger.debug("Gnome keyring is not available")
        return

    conf = SettingsController.get_instance()
    prefs = conf.get_prefs()
    if AUTH_DONT_ASK_KEY in prefs and get_boolean(prefs[AUTH_DONT_ASK_KEY]) == True:
        return
    
    if get_keyring().get_id() == gkeyring.GNOME_KEYRING_ID:
        return

    label = Gtk.Label()
    label.set_markup(_("""<b>Security warning</b>

You have gnome-keyring installed but your are using plain text encryption
to store your passwords. You can select the encryption method
in the preferences dialog.

"""))
    dialog = Gtk.Dialog(APP_LONG_NAME,
                       None,
                       Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT,
                       (Gtk.STOCK_OK, Gtk.RESPONSE_ACCEPT))
    dialog.set_icon(get_cloudsn_icon())
    dialog.vbox.pack_start(label)
    checkbox = Gtk.CheckButton(_("Don't ask me again"))
    checkbox.show()
    dialog.vbox.pack_end(checkbox)
    label.show()
    response = dialog.run()
    dialog.destroy()
    if checkbox.get_active():
        conf.set_pref (AUTH_DONT_ASK_KEY, True)
        conf.save_prefs()

