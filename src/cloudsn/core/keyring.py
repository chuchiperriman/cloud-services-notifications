# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-

# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from keyrings.base64keyring import Base64Keyring
from keyrings.plainkeyring import PlainKeyring

class Keyring(object):

    def has_credentials(self, acc):
        return False

    def load_credentials(self, acc):
        """
        Get the account info and set the user and password
        """
        pass

    def remove_credentials(self, acc):
        """ Remove the credentials from the keyring"""
        pass

    def store_credentials(self, acc):
        """ Save the credentials in the keyring"""
        pass

class KeyringManager:

    __default = None

    managers = []

    def __init__(self):
        if KeyringManager.__default:
           raise KeyringManager.__default
           
    @staticmethod
    def get_instance():
        if not KeyringManager.__default:
            KeyringManager.__default = KeyringManager()
            KeyringManager.__default.add_manager (PlainKeyring())
            KeyringManager.__default.add_manager (Base64Keyring())
        return KeyringManager.__default

    def add_manager (self, manager):
        self.managers.append (manager)
    def get_managers (self):
        return self.managers
    def get_manager(self, name):
        for man in self.managers:
            if man.get_name() == name:
                return man
        return None
    def get_manager_for_account(self, acc):
        for man in self.managers:
            if man.has_credentials(acc)
                return man
        return None
        
class KeyringException(Exception): pass
