from cloudsn.providers import tweepy
from providersbase import ProviderUtilsBuilder
from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.keyring import Credentials
from cloudsn.core.provider import Provider
from cloudsn.core import utils
from gi.repository import GObject
from gi.repository import Gtk

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
        if not "since_id" in acc:
            acc["since_id"] = -1
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
        if "since_id" in account and account["since_id"] != -1:
            since_id = account["since_id"]

        messages = api.home_timeline(since_id=since_id)

        if len(messages) < 1:
            account.new_unread = []
            return

        news = []
        if since_id:
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
        account["since_id"] = messages[0].id
        GObject.idle_add(self.__save_account, account)
        
    def __save_account(self, account):
        AccountManager.get_instance().save_account(account)
        return False
        
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

