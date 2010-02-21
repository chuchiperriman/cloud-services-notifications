from cloudsn import logger

notifications = []
disable = True
notifying = False

try:
    import pynotify
    if pynotify.init("Cloud Services Notifications"):
        disable = False
    else:
        logger.error("Cannot initialize libnotify")
except Exception, e:
    logger.exception ("there was a problem initializing the pynotify module: %s" % (e))


def notify_closed_cb (n, data=None):
    global notifications, notifying
    
    notifying = False
    notifications.remove (n)
    n = None
    notify_process()

def notify_process ():
    global notifications, notifying

    if notifying == True or len(notifications) == 0:
        return
        
    n = notifications[0]
    n.connect("closed", notify_closed_cb)
    n.show()
    
    notifying= True

def notify (title, message, icon = None):
    if disable == True:
        raise NotificationError ("there was a problem initializing the pynotify module")
        
    global notifications
    n = pynotify.Notification(title, message)
    n.set_urgency(pynotify.URGENCY_LOW)
    n.set_timeout(8000)
    
    if icon:
        n.set_icon_from_pixbuf(icon)

    notifications.append(n)
    notify_process()

class NotificationError(Exception): pass
