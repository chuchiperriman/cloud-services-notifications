class AccountData:
    def __init__ (self, name, provider):
        self.unread = 0
        self.new_unread = 0
        self.properties = {}
        self.properties["name"] = name
        self.properties["provider_name"] = provider.get_name()
        self.provider = provider
        
    def __getitem__(self, key):
        return self.properties[key]

    def __setitem__(self, key, value):
        self.properties[key] = value

    def get_properties(self):
        return self.properties
    
    def get_name (self):
        return self.properties["name"]

    def get_provider (self):
        return self.provider

    def get_unread (self):
        return self.unread

    def get_new_unread (self):
        return self.new_unread

    def update (self):
        self.provider.update_account (self)

class AccountManager:
    def __init__(self):
        self.accounts = {}
        
    def add_account(self, account):
        self.accounts[account.get_name()] = account

    def get_account(self, account_name):
        return self.accounts[account_name]

_account_manager = None

def GetAccountManager():
    global _account_manager
    if _account_manager is None:
        _account_manager = AccountManager()
    return _account_manager
    
