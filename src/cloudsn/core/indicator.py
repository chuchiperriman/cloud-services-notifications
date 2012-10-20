import os
from cloudsn.core import config, utils, notification
from cloudsn import logger

class Indicator:

    def get_name(self):
        return None

    def set_active(self, active):
        pass
    def create_indicator(self, acc):
        pass

    def update_account(self, acc):
        pass

    def remove_indicator(self, acc):
        pass
    
    def update_error(self, acc):
        pass

class IndicatorManager():

    __default = None

    def __init__(self):
        if IndicatorManager.__default:
           raise IndicatorManager.__default

        self.indicator= None
        self.indicators = {}
        from cloudsn.ui.indicators import statusicon
        indi_statusicon = statusicon.StatusIconIndicator()
        self.indicators[indi_statusicon.get_name()] = indi_statusicon
        indi_indicator = None
        try:
            from cloudsn.ui.indicators import indicatorapplet
            indi_indicator = indicatorapplet.IndicatorApplet()
            self.indicators[indi_indicator.get_name()] = indi_indicator
        except Exception,e:
            logger.exception("The indicator applet provider cannot be loaded: %s", e)
            
        indi_messagingmenu = None
        try:
            from cloudsn.ui.indicators import messagingmenu
            indi_messagingmenu = messagingmenu.IndicatorApplet()
            self.indicators[indi_messagingmenu.get_name()] = indi_messagingmenu
        except Exception,e:
            logger.exception("The message menu applet provider cannot be loaded: %s", e)

        self.config = config.SettingsController.get_instance()
        indicator_conf = self.config.get_prefs()["indicator"]
        if indicator_conf:
            for name in self.indicators:
                if name == indicator_conf:
                    self.indicator = self.indicators[name]
                    break
            if not self.indicator:
                logger.error("The indicator named %s is configured but it cannot be found" % (indicator_conf))
                notification.notify (_("Indicator error"),
                                    _("The indicator named %s is configured but it cannot be found") % (indicator_conf),
                                    utils.get_error_pixbuf())
        if not self.indicator:
            if "DESKTOP_SESSION" in os.environ and os.environ["DESKTOP_SESSION"] == 'ubuntu':
                indi_fin = indi_messagingmenu if indi_messagingmenu else indi_indicator
                if not indi_fin:
                    notification.notify (_("Indicator error"),
                                        _("The indicator for ubuntu cannot be loaded "),
                                        utils.get_error_pixbuf())
                    raise Error(_("The indicator for ubuntu cannot be loaded "))
                self.indicator = indi_fin
            else:
                self.indicator = indi_statusicon
            
        self.indicator.set_active(True)
        
    @staticmethod
    def get_instance():
        if not IndicatorManager.__default:
            IndicatorManager.__default = IndicatorManager()
        return IndicatorManager.__default
    
    def get_indicator(self):
        return self.indicator

    def get_indicators(self):
        return self.indicators.values()
