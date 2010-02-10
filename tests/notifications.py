import pynotify
if pynotify.init("Cloud Services Notifications"):
    n = pynotify.Notification("Cloudsn", "Mensaje de notificacion")
    n.set_urgency(pynotify.URGENCY_LOW)
    n.set_timeout(4000)
#    if icon:
#        n.set_icon_from_pixbuf(icon)
    n.show()
else:
    raise NotificationError ("there was a problem initializing the pynotify module")

