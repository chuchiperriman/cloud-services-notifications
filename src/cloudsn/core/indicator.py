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

class IndicatorManager():

    __default = None

    def __init__(self):
        if IndicatorManager.__default:
           raise IndicatorManager.__default

        self.indicators = {}
        #TODO Use the correct indicator
        from cloudsn.ui.indicators import statusicon
        indi = statusicon.StatusIconIndicator()
        self.indicators[indi.get_name()] = indi
        self.indicator = indi
        try:
            from cloudsn.ui.indicators import indicatorapplet
            indi = indicatorapplet.IndicatorApplet()
            self.indicators[indi.get_name()] = indi
            self.indicator = indi
        except Exception,e:
            logger.exception("The indicator applet provider cannot be loaded: %s", e)

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
