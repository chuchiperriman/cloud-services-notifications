import config

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

    def save_conf(self):
        sc = config.GetSettingsController()
        sc.set_account_config (self)
        sc.save_accounts()

    def del_conf(self):
        sc = config.GetSettingsController()
        sc.del_account_config(self.get_name())
        sc.save_accounts()

class AccountManager:
    def __init__(self):
        self.accounts = {}
    
    def add_account(self, account, store=False):
        self.accounts[account.get_name()] = account
        if store:
            account.save_conf()

    def get_account(self, account_name):
        return self.accounts[account_name]

    def get_accounts(self):
        return self.accounts.values()

    def del_account(self, account, complete=True):
        del self.accounts[account.get_name()]
        if complete:
            account.del_conf()

_account_manager = None

def GetAccountManager():
    global _account_manager
    if _account_manager is None:
        _account_manager = AccountManager()
    return _account_manager
    
