import gconf
import os
import subprocess

def show_url(url):
    """Open any @url with default viewer"""
    from gtk import show_uri, get_current_event_time
    from gtk.gdk import screen_get_default
    from glib import GError
    try:
            show_uri(screen_get_default(), url, get_current_event_time())
    except GError, e:
            print "Error in gtk.show_uri:", e

def invoke_subprocess(cmdline):
	setsid = getattr(os, 'setsid', None)
	subprocess.Popen(cmdline, close_fds = True, preexec_fn = setsid)

def get_default_mail_reader():
	client = gconf.client_get_default()
	cmd  = client.get_string("/desktop/gnome/url-handlers/mailto/command")
	return cmd.split()[0]

def open_mail_reader():
	cmdline = get_default_mail_reader()
	invoke_subprocess(cmdline)

if __name__ == "__main__":
    print get_default_mail_reader()
    open_mail_reader()
