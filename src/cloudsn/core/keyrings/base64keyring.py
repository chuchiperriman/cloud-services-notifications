# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
import base64
import gettext
from cloudsn import logger
from ..keyring import Keyring, KeyringException, Credentials

class Base64Keyring(Keyring):

    def get_id(self):
        return "base64"
        
    def get_name(self):
        return _("Base64 encoding")

    def remove_credentials(self, acc):
        del(acc["username"])
        del(acc["password"])
        
    def store_credentials(self, acc, credentials):
        try:
            logger.debug("Storing base64 credentials for account: %s" % (acc.get_name()))
            acc["username"] = base64.encodestring(credentials.username)
            acc["password"] = base64.encodestring(credentials.password)
        except Exception, e:
            raise KeyringException("Cannot encode the base64 username password for account %s" % (acc.get_name()), e)

    def get_credentials(self, acc):
        self.__check_valid(acc)
        try:
            return Credentials(base64.decodestring(acc["username"]),
                base64.decodestring(acc["password"]))
        except Exception, e:
            raise KeyringException("Cannot decode the base64 username or password for account %s" % (acc.get_name()), e)
            
    def __check_valid(self, acc):
        if not "username" in acc or not "password" in acc:
            raise KeyringException("The account %s has not a username or password configured" % (acc.get_name()))

