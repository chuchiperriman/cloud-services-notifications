import tweepy
from providersbase import ProviderUtilsBuilder
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.core.provider import Provider
from cloudsn.core import utils
from cloudsn.core import config
import gtk

class IdenticaProvider(ProviderUtilsBuilder):

    __default = None

    def __init__(self, name = "Identi.ca", id_provider = "identica", activate_url = "http://identi.ca"):
        ProviderUtilsBuilder.__init__(self, name, id_provider)
        self.activate_url = activate_url
        
    @staticmethod
    def get_instance():
        if not IdenticaProvider.__default:
            IdenticaProvider.__default = IdenticaProvider()
        return IdenticaProvider.__default

    def load_account(self, props):
        acc = IdenticaAccount(props, self)
        acc.properties["activate_url"] = self.activate_url
        acc.last_id = -1
        return acc

    def get_dialog_def (self):
        return [{"label": "User", "type" : "str"},
                {"label": "Password", "type" : "pwd"}]

    def populate_dialog(self, widget, acc):
        credentials = acc.get_credentials_save()
        self._set_text_value ("User",credentials.username)
        self._set_text_value ("Password", credentials.password)

    def set_account_data_from_widget(self, account_name, widget, account=None):
        username = self._get_text_value ("User")
        password = self._get_text_value ("Password")
        if username=='' or password=='':
            raise Exception(_("The user name and the password are mandatory"))

        if not account:
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'activate_url' : self.activate_url}
            account = self.load_account(props)

        account.set_credentials(Credentials(username, password))

        return account

    def get_api(self, account):
        credentials = account.get_credentials()
        auth = tweepy.BasicAuthHandler(credentials.username, credentials.password)
        api = tweepy.API(auth, "identi.ca",api_root="/api")
        return api
        
    def update_account (self, account):
        api = self.get_api(account)
        
        since_id = None
        if account.last_id != -1:
            since_id = account.last_id

        messages = api.home_timeline()

        if len(messages) < 1:
            account.new_unread = []
            return

        news = []
        if account.last_id != -1:
            for m in messages:
                if m.id not in account.notifications:
                    account.notifications[m.id] = m.id
                    news.append (Notification(m.id, m.text, m.user.screen_name,
                                 self.get_message_icon(m)))
        else:
            #If it is the fist update, show the last message only
            account.notifications[messages[0].id] = messages[0].id
            news.append (Notification(messages[0].id, messages[0].text,
                         messages[0].user.screen_name,
                         self.get_message_icon(messages[0])))

        account.new_unread = news;
        account.last_id = messages[0].id
        
    def get_message_icon(self,m):
        icon = None
        try:
            icon = utils.download_image_to_pixbuf(m.user.profile_image_url)
        except Exception, e:
            logger.exception("Error loading the user avatar",e)

        return icon

class IdenticaAccount (AccountCacheMails):

    def __init__(self, properties, provider):
        AccountCacheMails.__init__(self, properties, provider)

    def get_total_unread (self):
        return 0

