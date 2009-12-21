from account import AccountData
from greaderatom import GreaderAtom
from provider import Provider
import config
import gtk
import utils

ICON = "/home/perriman/dev/cloud-services-notifications/data/greader.png"

_provider = None

class GReaderProvider(Provider):
    accounts = None
    def __init__(self):
        Provider.__init__(self, "Google Reader")
        self.icon = gtk.gdk.pixbuf_new_from_file(ICON)

    def get_accounts (self):
        if self.accounts is None:
            sc = config.GetSettingsController()
            self.accounts = []
            for account_name in sc.get_account_list():
                if sc.get_account_value (account_name, "type") != "greader":
                    continue
                account = GReaderAccount (account_name)
                account.username = sc.get_account_value (account_name, "username")
                account.password = sc.get_account_value (account_name, "password")
                self.accounts.append (account)
                
        return self.accounts

    def update_account (self, account):
        g = GreaderAtom (account.username, account.password)
        g.refreshInfo()
        account.unread = g.getTotalUnread()

def GetGReaderProvider ():
    global _provider
    if _provider is None:
        _provider = GReaderProvider()
    return _provider

class GReaderAccount (AccountData):
    def __init__(self, name):
        AccountData.__init__(self, name, GetGReaderProvider())
    def activate (self):
        utils.show_url ("http://reader.google.com")  
