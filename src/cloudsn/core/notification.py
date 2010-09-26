from cloudsn import logger
from cloudsn.core.sound import Sound
from cloudsn.core import config
from datetime import datetime

notifications = []
disable = True
notifying = False
last_notify = tstart = datetime.now()

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
    if n in notifications:
        notifications.remove (n)
    n = None
    notify_process()

def notify_process ():
    global notifications, notifying, last_notify

    if len(notifications) == 0:
        return;

    if notifying == True:
        #See Bug #622021 on gnome
        diff = datetime.now() - last_notify
        if diff.seconds > 30:
            logger.debug("30 seconds from the last notification, reactivating")
            notifying = False
        else:
            return

    n = notifications[0]
    n.connect("closed", notify_closed_cb)
    n.show()

    notifying= True
    last_notify = datetime.now()
    #TODO Do it better and configuable
    sound = Sound()
    sound.play(config.add_data_prefix("drip.ogg"))

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

