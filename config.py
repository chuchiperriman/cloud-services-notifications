class SettingsController:
    pass;
    
_settings_controller = None
def GetSettingsController():
        global _settings_controller
        if _settings_controller is None:
                _settings_controller = SettingsController()
        return _settings_controller
