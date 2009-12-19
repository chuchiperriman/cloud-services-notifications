import provider
import indicate
import time

class Controller:
    def __init__(self):
        self.prov_manager = provider.GetProviderManager()
        
    def load_providers (self):
        from gmailprovider import GMailProvider
        self.prov_manager.add_provider (GMailProvider())

    def init_indicator_server(self):
        server = indicate.indicate_server_ref_default()
        server.set_type("message.im")
        #To connect the click in the server name
        #server.connect("server-display", server_display)
        server.set_desktop_file("/home/perriman/dev/cloud-services-notifications/data/cloudsn.desktop")
        server.show()

    def create_indicator(self, account):
        indicator = indicate.Indicator()
        indicator.set_property("name", account.get_name())
        indicator.set_property_time("time", time.time())
        indicator.set_property_int("count", account.get_unread())
        indicator.show()
	    #indicator.connect("user-display", display)
    
    def start(self):
        self.load_providers()
        self.init_indicator_server()
        for provider in self.prov_manager.get_providers():
            for account in provider.get_accounts():
                self.create_indicator(account)

_controller = None

def GetController():
    global _controller
    if _controller is None:
        _controller = Controller()
    return _controller

