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
        #TODO Use the correct indicator
        from cloudsn.ui.indicators import statusicon
        statusindi = statusicon.StatusIconIndicator()
        self.indicators[statusindi.get_name()] = statusindi
        indiapplet = None
        try:
            from cloudsn.ui.indicators import indicatorapplet
            indiapplet = indicatorapplet.IndicatorApplet()
            self.indicators[indiapplet.get_name()] = indiapplet
        except Exception,e:
            logger.exception("The indicator applet provider cannot be loaded: %s", e)

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
            if indiapplet:
                self.indicator = indiapplet
            else:
                self.indicator = statusindi
            
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
