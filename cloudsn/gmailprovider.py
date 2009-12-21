from account import AccountData
from gmailatom import GmailAtom
from provider import Provider
import config
import gtk
import utils

ICON = "/home/perriman/dev/cloud-services-notifications/data/gmail.png"

_provider = None

class GMailProvider(Provider):
    accounts = None
    def __init__(self):
        Provider.__init__(self, "GMail")
        self.icon = gtk.gdk.pixbuf_new_from_file(ICON)

    def get_accounts (self):
        if self.accounts is None:
            sc = config.GetSettingsController()
            self.accounts = []
            for account_name in sc.get_account_list():
                if sc.get_account_value (account_name, "type") != "gmail":
                    continue
                account = GMailAccount (account_name)
                account.username = sc.get_account_value (account_name, "username")
                account.password = sc.get_account_value (account_name, "password")
                self.accounts.append (account)
                
        return self.accounts

    def update_account (self, account):
        g = GmailAtom (account.username, account.password)
        g.refreshInfo()
        """
        if g.getUnreadMsgCount () > 0:
            message = ""
            for i in range (g.getUnreadMsgCount ()):
                message += "- \n" + g.getMsgTitle (i) + "\n"
        """
        account.unread = g.getUnreadMsgCount ()

def GetGMailProvider ():
    global _provider
    if _provider is None:
        _provider = GMailProvider()
    return _provider

class GMailAccount (AccountData):
    def __init__(self, name):
        AccountData.__init__(self, name, GetGMailProvider())
    
    def activate (self):
        utils.show_url ("http://gmail.google.com")
