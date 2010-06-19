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
            #KeyringManager.__default.add_manager (GnomeKeyring())
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
        
