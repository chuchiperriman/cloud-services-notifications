from .twitterprovider import TwitterProvider
from cloudsn.core.provider import Provider
from cloudsn.core import utils
from cloudsn.core import config
import gtk

class IdenticaProvider(TwitterProvider):

    __default = None

    def __init__(self):
        if IdenticaProvider.__default:
           raise IdenticaProvider.__default
        TwitterProvider.__init__(self, "Identi.ca", "identica",
            "http://identi.ca", "http://identi.ca/api/")

    @staticmethod
    def get_instance():
        if not IdenticaProvider.__default:
            IdenticaProvider.__default = IdenticaProvider()
        return IdenticaProvider.__default

    def get_import_error(self):
        return None

