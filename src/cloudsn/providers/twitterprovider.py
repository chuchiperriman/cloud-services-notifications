from cloudsn.core.account import AccountCacheMails, AccountManager, Notification
from cloudsn.core.provider import Provider
from cloudsn.core import utils
from cloudsn.core import config
from cloudsn.providers import twitter
import gtk

class TwitterProvider(Provider):

    __default = None

    def __init__(self, name = "Twitter", icon = "twitter.png",
                activate_url = "http://twitter.com",
                api_url = "http://twitter.com"):
        Provider.__init__(self, name)
        self.icon = gtk.gdk.pixbuf_new_from_file(config.add_data_prefix(icon))
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

    def _create_dialog(self, parent):
        builder=gtk.Builder()
        builder.set_translation_domain("cloudsn")
        builder.add_from_file(config.add_data_prefix("greader-account.ui"))
        dialog = builder.get_object("dialog")
        dialog.set_icon(self.get_icon())
        dialog.set_transient_for(parent)
        return (builder, dialog)
        
    def create_account_dialog(self, account_name, parent):
        builder, dialog = self._create_dialog(parent)
        account = None
        if dialog.run() == 0:
            username = builder.get_object("username_entry").get_text()
            password = builder.get_object("password_entry").get_text()
            props = {'name' : account_name, 'provider_name' : self.get_name(),
                'username' : username, 'password' : password,
                'activate_url' : self.activate_url}
            account = self.load_account(props)
        dialog.destroy()
        return account
        
    def edit_account_dialog(self, acc, parent):
        res = False
        builder, dialog = self._create_dialog(parent)
        builder.get_object("username_entry").set_text(acc["username"])
        builder.get_object("password_entry").set_text(acc["password"])
        account = None
        if dialog.run() == 0:
            acc["username"] = builder.get_object("username_entry").get_text()
            acc["password"] = builder.get_object("password_entry").get_text()
            res = True
        dialog.destroy()
        return res

class TwitterAccount (AccountCacheMails):

    def __init__(self, properties, provider):
        AccountCacheMails.__init__(self, properties, provider)

    def get_total_unread (self):
        return 0
