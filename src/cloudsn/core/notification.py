class NotificationError(Exception): pass

def notify (title, message, icon = None):
    import pynotify
    if pynotify.init("Cloud Services Notifications"):
        n = pynotify.Notification(title, message)
        n.set_urgency(pynotify.URGENCY_LOW)
        n.set_timeout(8000)
        
        #TODO In debian the messages are not shown in a queue
        #TODO Change it and do it better
        """
        try:
            from cloudsn.core import indicator
            from cloudsn.ui.indicators.statusicon import StatusIconIndicator
            ind = indicator.IndicatorManager.get_instance().get_indicator()
            if isinstance(ind, StatusIconIndicator):
                print ind.statusIcon
                n.attach_to_status_icon (ind.statusIcon)
        except Exception, e:
            print e
            pass;
        """
        if icon:
            n.set_icon_from_pixbuf(icon)
        n.show()
    else:
        raise NotificationError ("there was a problem initializing the pynotify module")

