from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.providers.providersbase import ProviderBase
from cloudsn.core import utils
from cloudsn.core import config
from cloudsn.providers import twitter
import gtk

class TwitterProvider(ProviderBase):

    __default = None

    def __init__(self, name = "Twitter", id_provider = None, activate_url = "http://twitter.com",
                api_url = "http://twitter.com"):
        ProviderBase.__init__(self, name, id_provider)
        self.activate_url = activate_url
        self.api_url = api_url

    @staticmethod
    def get_instance():
        if not TwitterProvider.__default:
            TwitterProvider.__default = TwitterProvider()
        return TwitterProvider.__default

    def load_account(self, props):
        acc = TwitterAccount(props, self)
        acc.properties["activate_url"] = self.activate_url
        acc.last_id = -1
        return acc

    def populate_dialog(self, builder, acc):
        self._set_text_value ("username_entry",acc["username"])
        self._set_text_value ("password_entry", acc["password"])
    
    def save_from_dialog(self, builder, account_name, acc = None):
        if not acc:
            username = self._get_text_value ("username_entry")
            password = self._get_text_value ("password_entry")
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'username' : username, 'password' : password,
                'activate_url' : self.activate_url}
            acc = self.load_account(props)
        else:
            acc["username"] = self._get_text_value ("username_entry")
            acc["password"] = self._get_text_value ("password_entry")
        
        return acc
        
    def update_account (self, account):
        
        api = twitter.Api(username=account['username'],
            password=account['password'],
            base_url=self.api_url)
        #base_url="identi.ca/api/"

        since_id = None
        if account.last_id != -1:
            since_id = account.last_id
            
        messages = api.GetFriendsTimeline(since_id=since_id)
        
        if len(messages) < 1:
            account.new_unread = []
            return

        news = []
        if account.last_id != -1:
            for m in messages:
                if m.id not in account.notifications:
                    account.notifications[m.id] = m.id
                    news.append (Notification(m.id, m.text, m.user.screen_name))
        else:
            #If it is the fist update, show the last message only
            account.notifications[messages[0].id] = messages[0].id
            news.append (Notification(messages[0].id, messages[0].text, messages[0].user.screen_name))
        
        account.new_unread = news;
        account.last_id = messages[0].id



class TwitterAccount (AccountCacheMails):

    def __init__(self, properties, provider):
        AccountCacheMails.__init__(self, properties, provider)

    def get_total_unread (self):
        return 0
