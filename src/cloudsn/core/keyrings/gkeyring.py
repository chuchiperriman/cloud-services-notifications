# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
import gnomekeyring as gk
from ..keyring import Keyring, KeyringException, Credentials
from cloudsn import logger
import threading

GNOME_KEYRING_ID = "gnomekeyring"

class GnomeKeyring(Keyring):

    _KEYRING_NAME = 'cloudsn'
    
    def __init__(self):
        self._protocol = "network"
        self._key = gk.ITEM_NETWORK_PASSWORD
        if not gk.is_available():
            raise KeyringException("The Gnome keyring is not available")
        logger.debug("default keyring ok")
        self.loaded = False
        self.lock = threading.RLock()
        
    def __check_keyring (self):
        if not self.loaded:
            try:
                gk.list_item_ids_sync(self._KEYRING_NAME)
            except Exception, e:
                logger.exception("Error getting the gnome keyring. We'll try to create it: %s",e)
                logger.debug("Creating keyring " + self._KEYRING_NAME)
                gk.create_sync(self._KEYRING_NAME, None)
            self.loaded = True
        
    def get_id(self):
        return GNOME_KEYRING_ID
        
    def get_name(self):
        return _("Gnome keyring")

    def get_credentials(self, acc):
        self.lock.acquire()
        try:
            logger.debug("Getting credentials with gnome keyring for account %s" % (acc.get_name()))
            attrs = {"account_name": acc.get_name()}
            try:
                items = gk.find_items_sync(gk.ITEM_NETWORK_PASSWORD, attrs)
            except gk.NoMatchError, e:
                items = list()
            if len(items) < 1:
                raise KeyringException("Cannot find the keyring data for the account %s" % (acc.get_name()))
            
            logger.debug("items ok")
            return Credentials (items[0].attributes["username"], items[0].secret)
        finally:
            self.lock.release()

    def remove_credentials(self, acc):
        self.lock.acquire()
        try:
            logger.debug("Removing credentias from gnome keyring for the account: %s" % (acc.get_name()))
            if hasattr(acc, "keyringid"):
                gk.item_delete_sync(self._KEYRING_NAME, int(acc.keyringid))
                logger.debug("Credentials removed")
            else:
                logger.debug("The account has not credentials asigned, continue")
        finally:
            self.lock.release()

    def store_credentials(self, acc, credentials):
        self.lock.acquire()
        try:
            logger.debug("Storing credentials with gnome keyring for account %s" % (acc.get_name()))
            self.__check_keyring()
            #Remove the old info and create a new item with the new info
            self.remove_credentials(acc)
            attrs = {
                "account_name": acc.get_name(),
                "username": credentials.username,
                }
            id = gk.item_create_sync(self._KEYRING_NAME, \
                 gk.ITEM_NETWORK_PASSWORD, acc.get_name(), attrs, credentials.password, True)
            logger.debug("credentials stored with id: %i" % (id))
        finally:
            self.lock.release()
