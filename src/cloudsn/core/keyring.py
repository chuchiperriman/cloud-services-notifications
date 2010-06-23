# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.core import config

class Keyring(object):
    
    def get_name(self):
        return None

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
    
    current = None

    def __init__(self):
        if KeyringManager.__default:
            raise KeyringManager.__default
            
        self.config = config.SettingsController.get_instance()
        from keyrings.plainkeyring import PlainKeyring
        self.__add_manager (PlainKeyring())
        #from keyrings.base64keyring import Base64Keyring
        #self.__add_manager (Base64Keyring())
        configured_name = self.config.get_prefs()["keyring"]
        for m in self.managers:
            if m.get_name() == configured_name:
                self.current = m
                break
        if not self.current:
            #Plain by default
            self.current = self.managers[0]
        
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
        
class KeyringException(Exception): pass


