# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
import base64
from ..keyring import Keyring

class Base64Keyring(Keyring):

    def has_credentials(self, acc):
        if "keyring_name" in acc.get_properties() and \
            acc["keyring_name"] == "base64":
            return True
        return False

    def load_credentials(self, acc):
        self.__check_valid(acc)
        try:
            dec = base64.decodestring(acc["password"])
            acc["password"] = dec
        except Exception, e:
            raise KeyringException("Cannot decode the base64 password for account %s" % (acc.get_name()), e)
        
    def store_credentials(self, acc):
        self.__check_valid(acc)
        try:
            enc = base64.encodestring(password)
            acc["password"] = enc
        except Exception, e:
            raise KeyringException("Cannot encode the base64 password for account %s" % (acc.get_name()), e)

    def __check_valid(self, acc):
        if not self.has_credentials(acc):
            raise KeyringException("The account %s has not base64 encoding" % (acc.get_name()))
        
        if not "password" in acc.get_properties():
            raise KeyringException("The account %s has not a password configured" % (acc.get_name()))

