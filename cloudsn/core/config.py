import ConfigParser
import xdg.BaseDirectory as bd
import os
import gobject
import os

class SettingsController(gobject.GObject):

    __default = None

    __gtype_name__ = "SettingsController"

    # Section, Key, Value
    __gsignals__ = { "value-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, 
                                        (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT))}

    CONFIG_HOME = bd.xdg_config_home + '/cloud-services-notifications'
    CONFIG_PREFERENCES = CONFIG_HOME + '/preferences'
    CONFIG_ACCOUNTS = CONFIG_HOME + '/accounts'

    def __init__(self):
        if SettingsController.__default:
           raise SettingsController.__default
        gobject.GObject.__init__(self)
        self.ensure_config()
        self.config_prefs = ConfigParser.ConfigParser()
        self.config_prefs.read (self.CONFIG_PREFERENCES)
        self.config_accs = ConfigParser.ConfigParser()
        self.config_accs.read (self.CONFIG_ACCOUNTS)
        self.prefs = self.config_to_dict(self.config_prefs)
        self.accounts = self.config_to_dict(self.config_accs)

    @staticmethod
    def get_instance():
        if not SettingsController.__default:
            SettingsController.__default = SettingsController()
        return SettingsController.__default

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

    def get_account_list_by_provider (self, provider):
        res = []
        for sec in self.accounts.keys():
            if "provider_name" in self.accounts[sec]:
                if self.accounts[sec]["provider_name"] == provider.get_name():
                    res.append (sec)
            else:
                print "The account " + sec + " has not a provider_name property"
                
        return res
        
    def get_account_config (self, account_name):
        return self.accounts[account_name]

    def set_account_config(self, account):
        if account.get_name() in self.accounts:
            del self.accounts[account.get_name()]
        self.accounts[account.get_name()] = account.get_properties()
        
    def del_account_config (self, account_name):
        del self.accounts[account_name]
        
    def get_prefs (self):
        return self.prefs["preferences"]
        
    def set_pref (self, key, value):
        self.prefs["preferences"][key] = value
        self.emit("value-changed", "preferences", key, value)

    def save_prefs (self):
        self.dict_to_config(self.config_prefs, self.prefs)
        with open(self.CONFIG_PREFERENCES, 'wb') as configfile:
            self.config_prefs.write(configfile)

    def save_accounts (self):
        self.config_accs = ConfigParser.ConfigParser()
        self.dict_to_config(self.config_accs, self.accounts)
        with open(self.CONFIG_ACCOUNTS, 'wb') as configfile:
            self.config_accs.write(configfile)

def get_data_dir ():
    return os.path.abspath ("./data")


