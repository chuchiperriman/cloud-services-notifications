from cloudsn.core import config
import gobject
from datetime import datetime
import gettext

class Notification:
    def __init__(self, id = None, message = None, sender = None):
        self.id = id
        self.sender = sender
        self.message = message

class Account:
    def __init__ (self, name, provider):
        self.properties = {}
        self.properties["name"] = name
        self.properties["provider_name"] = provider.get_name()
        self.provider = provider
        self.last_update = None
        
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

    def get_last_update (self):
        return self.last_update
        
    def get_total_unread (self):
        return 0

    def get_new_unread_notifications(self):
        return []

    def update (self):
        self.provider.update_account (self)
        self.last_update = datetime.now()

    def save_conf(self):
        sc = config.SettingsController.get_instance()
        sc.set_account_config (self)
        sc.save_accounts()

    def del_conf(self):
        sc = config.SettingsController.get_instance()
        sc.del_account_config(self.get_name())
        sc.save_accounts()
        
    def activate(self):
        logger.warn('This account type has not an activate action')

class AccountBase (Account):

    def __init__(self, name, username, password, provider, url=None):
        Account.__init__(self, name, provider)
        self["username"] = username
        self["password"] = password
        self.total_unread = 0
        self.notifications = None
        self.new_unread = []
        self.url = None

    def get_total_unread (self):
        if self.notifications:
            return len(self.notifications)
        else:
            return self.total_unread

    def get_new_unread_notifications(self):
        return self.new_unread
        
    def activate (self):
        if self.url:
            utils.show_url (url)
        else:
            super(AccountBase,self).activate()

class AccountManager (gobject.GObject):

    __default = None

    __gtype_name__ = "AccountManager"

    __gsignals__ = { "account-added" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
                     "account-deleted" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
                     "account-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}
    
    def __init__(self):
        if AccountManager.__default:
           raise AccountManager.__default
        gobject.GObject.__init__(self)
        self.accounts = {}

    @staticmethod
    def get_instance():
        if not AccountManager.__default:
            AccountManager.__default = AccountManager()
        return AccountManager.__default

    def validate_account(self, account_name):
        if account_name in self.accounts:
            error = _('The account %s already exists' % (account_name))
            raise Exception(error)
    
    def add_account(self, acc, store=False):
        self.validate_account(acc.get_name())
        self.accounts[acc.get_name()] = acc
        if store:
            acc.save_conf()

        self.emit("account-added", acc)

    def edit_account(self, account):
        account.save_conf()
        self.emit("account-changed", account)

    def get_account(self, account_name):
        return self.accounts[account_name]

    def get_accounts(self):
        return self.accounts.values()

    def del_account(self, account, complete=True):
        del self.accounts[account.get_name()]
        if complete:
            account.del_conf()
        self.emit("account-deleted", account)
        
