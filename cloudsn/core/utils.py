def show_url(url):
    """Open any @url with default viewer"""
    from gtk import show_uri, get_current_event_time
    from gtk.gdk import screen_get_default
    from glib import GError
    try:
            show_uri(screen_get_default(), url, get_current_event_time())
    except GError, e:
            print "Error in gtk.show_uri:", e
