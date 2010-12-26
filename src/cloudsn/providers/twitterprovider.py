from identicaprovider import IdenticaProvider
import tweepy

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
