class Indicator:
    def create_indicator(self, acc):
        pass;

    def update_account(self, acc):
        pass

    def remove_indicator(self, acc):
        pass

class IndicatorManager():

    __default = None

    def __init__(self):
        if IndicatorManager.__default:
           raise IndicatorManager.__default
        
        #TODO Use the correct indicator
        from cloudsn.ui.indicators import statusicon
        self.indicator = statusicon.StatusIconIndicator()
        
    @staticmethod
    def get_instance():
        if not IndicatorManager.__default:
            IndicatorManager.__default = IndicatorManager()
        return IndicatorManager.__default
    
    def get_indicator(self):
        return self.indicator

