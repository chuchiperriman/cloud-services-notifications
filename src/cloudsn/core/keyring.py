# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.core import config
from cloudsn import logger

class Credentials:
    def __init__(self, username = None, password = None):
        self.username = username
        self.password = password

class Keyring():

    def get_id(self):
        raise Exception("You must configure the keyring id")

    def get_name(self):
        return None

    def remove_credentials(self, acc):
        """ Remove the credentials from the keyring"""
        pass

    def store_credentials(self, acc, credentials):
        """ Save the credentials in the keyring"""
        pass

    def get_credentials(self, acc):
        """ Returns the credentials (Credentials) for the account """
        return None

class KeyringManager:

    __default = None

    managers = []

    current = None

    def __init__(self):
        if KeyringManager.__default:
            raise KeyringManager.__default

        #TODO control errors to disable providers
        self.config = config.SettingsController.get_instance()
        from keyrings.plainkeyring import PlainKeyring
        self.__add_manager (PlainKeyring())

        try:
            from keyrings.base64keyring import Base64Keyring
            self.__add_manager (Base64Keyring())
        except Exception, e:
            logger.exception("Cannot load base64 keyring: %s", e)
            
        try:
            from keyrings.gkeyring import GnomeKeyring
            self.__add_manager (GnomeKeyring())
        except Exception, e:
            logger.exception("Cannot load gnome keyring: %s", e)
        configured_name = self.config.get_prefs()["keyring"]
        for m in self.managers:
            if m.get_id() == configured_name:
                self.current = m
                logger.info("Current keyring: %s " % (self.current.get_name()))
                break
        if not self.current:
            #The most secure by default
            self.current = self.managers[-1]
            logger.info("No keyring configured, using %s " % (self.current.get_name()))

    @staticmethod
    def get_instance():
        if not KeyringManager.__default:
            KeyringManager.__default = KeyringManager()
        return KeyringManager.__default

    def __add_manager (self, manager):
        self.managers.append (manager)

    def get_managers (self):
        return self.managers

    def get_manager(self):
        return self.current

    def set_manager(self, manager):
        #The same manager, we don't need do nothing
        if manager == self.current:
            logger.debug("Setting the keyring manager but it is the same")
            return
        logger.info("Setting the keyring manager: %s" % (manager.get_name()))
        from cloudsn.core import account
        old = self.current
        for acc in account.AccountManager.get_instance().get_accounts():
            try:
                credentials = acc.get_credentials()
                old.remove_credentials(acc)
                manager.store_credentials(acc, credentials)
            except Exception, e:
                logger.exception("Cannot change the keyring for the account "\
                    + acc.get_name() + ": %s" , e)

        self.current = manager
        account.get_account_manager().save_accounts(False)


class KeyringException(Exception): pass

def get_keyring():
    return KeyringManager.get_instance().get_manager()

