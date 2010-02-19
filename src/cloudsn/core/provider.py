from cloudsn.core.account import Account

class Provider:
    
    def __init__ (self, name):
        self.name = name
        self.icon = None
        
    def load_account(self, props):
        return Account(props, self)
        
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
    def create_account_dialog(self, account_name, parent_window):
        """ Returns the new created account"""
        return None
    def edit_account_dialog(self, acc, parent_window):
        """ Returns True if the account has been changed"""
        return False

class ProviderManager:

    __default = None

    providers = []

    def __init__(self):
        if ProviderManager.__default:
           raise ProviderManager.__default
           
    @staticmethod
    def get_instance():
        if not ProviderManager.__default:
            ProviderManager.__default = ProviderManager()
            #Default providers
            from cloudsn.providers.gmailprovider import GMailProvider
            from cloudsn.providers.greaderprovider import GReaderProvider
            from cloudsn.providers.pop3provider import Pop3Provider
            from cloudsn.providers.imapprovider import ImapProvider
            from cloudsn.providers.twitterprovider import TwitterProvider
            ProviderManager.__default.add_provider (GMailProvider.get_instance())
            ProviderManager.__default.add_provider (GReaderProvider.get_instance())
            ProviderManager.__default.add_provider (Pop3Provider.get_instance())
            ProviderManager.__default.add_provider (ImapProvider.get_instance())
            ProviderManager.__default.add_provider (TwitterProvider.get_instance())
        return ProviderManager.__default

    def add_provider (self, provider):
        self.providers.append (provider)
    def get_providers (self):
        return self.providers
    def get_provider(self, name):
        for prov in self.providers:
            if prov.get_name() == name:
                return prov
        return None
        
