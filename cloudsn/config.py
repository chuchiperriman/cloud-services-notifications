import ConfigParser
import xdg.BaseDirectory as bd
import os
import gobject

class SettingsController(gobject.GObject):

    __gtype_name__ = "SettingsController"

    CONFIG_HOME = bd.xdg_config_home + '/cloud-services-notifications'
    CONFIG_PREFERENCES = CONFIG_HOME + '/preferences'
    CONFIG_ACCOUNTS = CONFIG_HOME + '/accounts'

    def __init__(self):
        gobject.GObject.__init__(self)
        self.ensure_config()
        self.config_prefs = ConfigParser.ConfigParser()
        self.config_prefs.read (self.CONFIG_PREFERENCES)
        self.config_accs = ConfigParser.ConfigParser()
        self.config_accs.read (self.CONFIG_ACCOUNTS)
        self.prefs = self.config_to_dict(self.config_prefs)
        self.accounts = self.config_to_dict(self.config_accs)

    def dict_to_config (self, config, dic):
        for sec, data in dic.iteritems():
            if not config.has_section(sec):
                config.add_section (sec)
            for key, value in data.iteritems():
                config.set(sec, key, value)
        
    def config_to_dict (self, config):
        res = {}
        for sec in config.sections():
            res[sec] = {}
            for key in config.options(sec):
                res[sec][key] = config.get(sec, key)
        return res
    
    def ensure_config (self):
        if not os.path.exists (self.CONFIG_HOME):
            os.makedirs (self.CONFIG_HOME)

        if not os.path.exists (self.CONFIG_ACCOUNTS):
            f = open(self.CONFIG_ACCOUNTS, "w")
            
        if not os.path.exists (self.CONFIG_PREFERENCES):
            f = open(self.CONFIG_PREFERENCES, "w")

    def get_account_list (self):
        return self.accounts.keys ()

    def get_account_list_by_type (self, acc_type):
        res = []
        for sec in self.accounts.keys():
            if self.accounts[sec]["type"] == acc_type:
                res.append (sec)
        return res
        
    def get_account_config (self, account):
        return self.accounts[account]

    def get_prefs (self):
        return self.prefs["preferences"]
        
    def set_pref (self, key, value):
        self.prefs["preferences"][key] = value
        self.emit("value-changed", "preferences", key, value)

    def save_prefs (self):
        self.dict_to_config(self.config_prefs, self.prefs)
        with open(self.CONFIG_PREFERENCES, 'wb') as configfile:
            self.config_prefs.write(configfile)

# Section, Key, Value
gobject.signal_new("value-changed", SettingsController, gobject.SIGNAL_RUN_LAST,
    gobject.TYPE_BOOLEAN, (gobject.TYPE_STRING, gobject.TYPE_STRING,
        gobject.TYPE_PYOBJECT))


_settings_controller = None

def GetSettingsController():
        global _settings_controller
        if _settings_controller is None:
                _settings_controller = SettingsController()
        return _settings_controller


def get_data_dir ():
    return "/home/perriman/dev/cloud-services-notifications/data"


