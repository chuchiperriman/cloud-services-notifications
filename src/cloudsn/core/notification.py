class NotificationError(Exception): pass

def notify (title, message, icon = None):
    import pynotify
    if pynotify.init("Cloud Services Notifications"):
        n = pynotify.Notification(title, message)
        n.set_urgency(pynotify.URGENCY_LOW)
        n.set_timeout(8000)
        if icon:
            n.set_icon_from_pixbuf(icon)
        n.show()
    else:
        raise NotificationError ("there was a problem initializing the pynotify module")

