import ConfigParser
import xdg.BaseDirectory as bd

class SettingsController:

    CONFIG_HOME = bd.xdg_config_home + '/cloud-services-notifications'
    CONFIG_FILE = CONFIG_HOME + '/configuration'
    
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read (self.CONFIG_FILE)

    def get_account_list (self):
        return ["Chuchiperriman","Tatina"]
        
    def get_account_items (self, account):
        return self.config.items (account)
        
    def get_account_value (self, account, key):
        return self.config.get (account, key)

_settings_controller = None

def GetSettingsController():
        global _settings_controller
        if _settings_controller is None:
                _settings_controller = SettingsController()
        return _settings_controller
