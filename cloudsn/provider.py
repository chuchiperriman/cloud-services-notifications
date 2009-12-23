class Provider:

    icon = None
    
    def __init__ (self, name):
        self.name = name
    def get_accounts (self):
        pass;
    def update_account (self, account_data):
        pass;
    def has_indicator(self):
        return True
    def has_notifications (self):
        return True
    def get_name (self):
        return self.name
    def get_icon (self):
        return self.icon

class ProviderManager:

    providers = []

    def add_provider (self, provider):
        self.providers.append (provider)
    def get_providers (self):
        return self.providers

_provider_manager = None

def GetProviderManager ():
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager
