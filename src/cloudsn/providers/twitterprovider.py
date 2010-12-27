from identicaprovider import IdenticaProvider
from cloudsn.core.keyring import Credentials
from cloudsn.core.account import AccountCacheMails
from cloudsn.core import config
import tweepy
import gtk

CONSUMER_KEY = 'uRPdgq7wqkiKmWzs9rneJA'
CONSUMER_SECRET = 'ZwwhbUl2mwdreaiGFd8IqUhfsZignBJIYknVA867Ieg'

class TwitterProvider(IdenticaProvider):

    __default = None

    def __init__(self):
        IdenticaProvider.__init__(self, "Twitter", "twitter", "http://twitter.com")

    @staticmethod
    def get_instance():
        if not TwitterProvider.__default:
            TwitterProvider.__default = TwitterProvider()
        return TwitterProvider.__default

    def get_api(self, account):
        credentials = account.get_credentials()
        ACCESS_KEY = credentials.username
        ACCESS_SECRET = credentials.password
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        return tweepy.API(auth)
        
    def get_account_data_widget (self, account=None):
        self.conf_widget = TwitterPrefs(account, self)
        return self.conf_widget.load()

    def set_account_data_from_widget(self, account_name, widget, account=None):
        return self.conf_widget.set_account_data(account_name)
        
        
class TwitterPrefs:

    def __init__(self, account, provider):
        self.account = account
        self.provider = provider

    def load(self):
        self.builder=gtk.Builder()
        self.builder.set_translation_domain("cloudsn")
        self.builder.add_from_file(config.add_data_prefix("twitter-account.ui"))
        self.box = self.builder.get_object("container")
        self.permission_button = self.builder.get_object("permission_button")
        self.pin_entry = self.builder.get_object("pin_entry")
        
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth_url = self.auth.get_authorization_url()
        self.permission_button.set_uri(auth_url)
        
        self.builder.connect_signals(self)
        if self.account:
            #Do not support editting
            pass
        return self.box

    def set_account_data (self, account_name):
        pin = self.pin_entry.get_text()
        if pin=='':
            raise Exception(_("The PIN is mandatory to set the Twitter account"))

        self.auth.get_access_token(pin)
        access_key = self.auth.access_token.key
        access_secret = self.auth.access_token.secret
        if not self.account:
            props = {"name" : account_name, "provider_name" : self.provider.get_name()}
            self.account = AccountCacheMails(props, self.provider)
            self.account.notifications = {}

        credentials = Credentials(access_key, access_secret)
        self.account.set_credentials(credentials)

        return self.account
        
