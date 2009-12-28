class Provider:
    
    def __init__ (self, name):
        self.name = name
        self.icon = None
    def get_accounts (self):
        pass
    def update_account (self, account_data):
        pass
    def has_indicator(self):
        return True
    def has_notifications (self):
        return True
    def get_name (self):
        return self.name
    def get_icon (self):
        return self.icon
    def create_account_dialog(self, account_name):
        """ Returns the new created account"""
        return None

class ProviderManager:

    providers = []

    def add_provider (self, provider):
        self.providers.append (provider)
    def get_providers (self):
        return self.providers
    def get_provider(self, name):
        for prov in self.providers:
            if prov.get_name() == name:
                return prov
        return None
        

_provider_manager = None

def GetProviderManager ():
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
        #Default providers
        from gmailprovider import GMailProvider
        from greaderprovider import GReaderProvider
        _provider_manager.add_provider (GMailProvider())
        _provider_manager.add_provider (GReaderProvider())
        
    return _provider_manager



