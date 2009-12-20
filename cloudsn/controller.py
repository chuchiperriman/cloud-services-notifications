import provider
import indicate
from time import time

class Controller:

    accounts = []
    
    def __init__(self):
        self.prov_manager = provider.GetProviderManager()
        
    def load_providers (self):
        from gmailprovider import GMailProvider
        self.prov_manager.add_provider (GMailProvider())

    def init_indicator_server(self):
        self.server = indicate.indicate_server_ref_default()
        self.server.set_type("message.im")
        #To connect the click in the server name
        #server.connect("server-display", server_display)
        self.server.set_desktop_file("/home/perriman/dev/cloud-services-notifications/data/cloudsn.desktop")
        self.server.show()

    def create_indicator(self, account):
        indicator = indicate.Indicator()
        indicator.set_property("name", account.get_name())
        indicator.set_property_time("time", time())
        indicator.set_property_int("count", account.get_unread())
        if account.get_provider().get_icon() is not None:
            indicator.set_property_icon("icon", account.get_provider().get_icon())
        indicator.show()
        #indicator.connect("user-display", display)
        account.indicator = indicator
    
    def start(self):
        self.load_providers()
        self.init_indicator_server()
        for provider in self.prov_manager.get_providers():
            for account in provider.get_accounts():
                account.update()
                self.create_indicator(account)

_controller = None

def GetController():
    global _controller
    if _controller is None:
        _controller = Controller()
    return _controller

