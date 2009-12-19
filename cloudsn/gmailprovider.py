from account import AccountData
from gmailatom import GmailAtom
from provider import Provider
import config

_provider = None

class GMailProvider(Provider):
    __provider_name__ = 'GMail'
    __provider_description = 'Check GMail accounts'

    def __init__(self):
        Provider.__init__(self, "GMail")

    def get_accounts (self):
        accounts = []
        sc = config.GetSettingsController()
        for account_name in sc.get_account_list():
            account = GMailAccount (account_name)
            account.username = sc.get_account_value (account_name, "username")
            account.password = sc.get_account_value (account_name, "password")
            accounts.append (account)
        return accounts

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
        
