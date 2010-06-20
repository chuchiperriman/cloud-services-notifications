# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from ..keyring import Keyring
import gettext

class PlainKeyring(Keyring):
    
    def get_name(self):
        return _("Plain text")

    def has_credentials(self, acc):
        if not "keyring_name" in acc.get_properties():
            return True
        if acc["keyring_name"] == "plain":
            return True
        return False

    def load_credentials(self, acc):
        self.__check_valid(acc)
        
    def store_credentials(self, acc):
        self.__check_valid(acc)

    def __check_valid(self, acc):
        if not self.has_credentials(acc):
            raise KeyringException("The account %s has not base64 encoding" % (acc.get_name()))
