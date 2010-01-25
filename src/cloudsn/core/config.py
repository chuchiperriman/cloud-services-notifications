import ConfigParser
import xdg.BaseDirectory as bd
import os
import sys
from os import mkdir
from os.path import isdir, join, dirname, abspath
import gobject
import gtk
import gettext


#Test if it is the tar/git
if os.path.exists(join (dirname (__file__), "../../../setup.py")):
    _base_prefix = abspath(join (dirname (__file__), "../../.."))
    _prefix = abspath (join (dirname (__file__), "../../../data"))
    _installed = False
else:
    for pre in ("site-packages", "dist-packages", sys.prefix):
        # Test if we are installed on the system
        for sub in ("share", "local/share"):
            _prefix = join (sys.prefix, sub, "cloudsn")
            _base_prefix = join (sys.prefix, sub)
            if isdir(_prefix):
                _installed = True
                break
        else:
            raise Exception(_("Can't find the cloudsn data directory"))

def get_base_data_prefix ():
    return abspath (_base_prefix)

def get_data_prefix ():
    return abspath (_prefix)

def add_data_prefix (subpath):
    return abspath (join (_prefix, subpath))

def is_installed ():
    return _installed

def get_apps_prefix():
    if is_installed():
        return abspath (join (_base_prefix, "applications"))
    else:
        return get_data_prefix()

def add_apps_prefix(subpath):
    return join (get_apps_prefix(), subpath)

class SettingsController(gobject.GObject):

    __default = None

    __gtype_name__ = "SettingsController"

    # Section, Key, Value
    __gsignals__ = { "value-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_BOOLEAN, 
                                        (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT))}

    CONFIG_HOME = bd.xdg_config_home + '/cloud-services-notifications'
    CONFIG_PREFERENCES = CONFIG_HOME + '/preferences'
    CONFIG_ACCOUNTS = CONFIG_HOME + '/accounts'

    __default_prefs = {
        "preferences" : {"minutes" : 10}
    }

    def __init__(self):
        if SettingsController.__default:
           raise SettingsController.__default
        gobject.GObject.__init__(self)
        self.ensure_config()
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
            f.close()
            
        if not os.path.exists (self.CONFIG_PREFERENCES):
            f = open(self.CONFIG_PREFERENCES, "w")
            f.close()
            
        self.config_prefs = ConfigParser.ConfigParser()
        self.config_prefs.read (self.CONFIG_PREFERENCES)
        self.config_accs = ConfigParser.ConfigParser()
        self.config_accs.read (self.CONFIG_ACCOUNTS)
        
        def fill_parser(parser, defaults):
            for secname, section in defaults.iteritems():
                if not parser.has_section(secname):
                    parser.add_section(secname)
                for key, default in section.iteritems():
                    if isinstance(default, int):
                        default = str(default)
                    if not parser.has_option(secname, key):
                        parser.set(secname, key, default)
                    
        fill_parser(self.config_prefs, self.__default_prefs)

    def get_account_list (self):
        return self.accounts.keys ()

    def get_account_list_by_provider (self, provider):
        res = []
        for sec in self.accounts.keys():
            if "provider_name" in self.accounts[sec]:
                if self.accounts[sec]["provider_name"] == provider.get_name():
                    res.append (sec)
            else:
                logger.error("The account " + sec + " has not a provider_name property")
                
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

__cloudsn_icon = None
def get_cloudsn_icon():
    global __cloudsn_icon
    if not __cloudsn_icon:
        __cloudsn_icon = gtk.gdk.pixbuf_new_from_file(add_data_prefix('cloudsn.png'))
    return __cloudsn_icon

def get_startup_file_path():
    return abspath(join(bd.xdg_config_home, "autostart", "cloudsn.desktop"))


