#import gconf
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf
import os
import subprocess
from email.header import decode_header
from cloudsn.core import config
from cloudsn import logger
import tempfile
import urllib2

def show_url(url):
    """Open any @url with default viewer"""
    #from Gtk import show_uri, get_current_event_time
    #from Gtk.gdk import screen_get_default
    #from glib import GError
    try:
        Gtk.show_uri(Gdk.Screen.get_default(), url, Gtk.get_current_event_time())
    except:
        logger.exception("Error in Gtk.show_uri: %s")

def invoke_subprocess(cmdline):
	setsid = getattr(os, 'setsid', None)
	subprocess.Popen(cmdline, close_fds = True, preexec_fn = setsid)

def get_default_mail_reader():
	#client = gconf.client_get_default()
	client = Gio.Settings.new()
	cmd  = client.get_string("/desktop/gnome/url-handlers/mailto/command")
	return cmd.split()[0]

def open_mail_reader():
	cmdline = get_default_mail_reader()
	invoke_subprocess(cmdline)

def mime_decode(str):
    strn, encoding = decode_header(str)[0]
    if encoding is None:
        return strn
    else:
        return strn.decode(encoding, "replace")

def get_boolean (value):
    if isinstance (value,bool):
        return value
    elif isinstance (value, str):
        return value.strip().lower() == 'true'
    return False

def get_error_pixbuf():
    icons = Gtk.IconTheme.get_default()
    #TODO How can I set this value with gir ? l = Gtk.ICON_LOOKUP_USE_BUILTIN
    return icons.load_icon(Gtk.STOCK_DIALOG_ERROR, 32, 0)

def get_account_error_pixbuf (acc):
    original = acc.get_provider().get_icon().copy()
    error = GdkPixbuf.Pixbuf.new_from_file(config.add_data_prefix('error.png'))
    error.composite(original, 10, 10, 22, 22, 10, 10, 1.0, 1.0, GdkPixbuf.InterpType.HYPER, 220)
    return original

def get_account_error_gicon (acc):
    return Gio.FileIcon.new(Gio.File.new_for_path(config.add_data_prefix('error.png')))

def download_image_to_tmp(url):
    filename = url.replace('http://', '0_')
    filename = filename.replace('/', '_')
    fullname = os.path.join(tempfile.gettempdir(), filename)

    if os.path.exists(fullname):
        return fullname
        
    f = urllib2.urlopen(url).read()

    fich = open(fullname, 'w+')
    fich.write(f)
    fich.close()
    
    return fullname

def download_image_to_pixbuf(url):
    path = download_image_to_tmp(url)
    return GdkPixbuf.Pixbuf.new_from_file(path)

def execute_command(acc, command):
    open_command = replace_variables(acc, command)
    if open_command != "":
        os.system(open_command + " &")
        return True
    else:
        return False
    
def replace_variables(acc, command):
    _command = command
    available_variables = {"${account_name}": "'" + acc.get_name().replace("'", "") + "'"}
    for variable in available_variables:
        _command = _command.replace(variable, available_variables[variable])
        
    return _command

def get_safe_filename(name):
    return "".join([x for x in name.lower() if x.isalpha() or x.isdigit()])
    
if __name__ == "__main__":
    print get_default_mail_reader()
    open_mail_reader()

