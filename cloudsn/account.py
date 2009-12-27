class AccountData:
    def __init__ (self, name, provider):
        self.unread = 0
        self.new_unread = 0
        self.properties = {}
        self.properties["name"] = name
        self.properties["provider_name"] = provider.get_name()
        self.provider = provider
        
    def __getitem__(self, key):
        return self.properties[key]

    def __setitem__(self, key, value):
        self.properties[key] = value

    def get_properties(self):
        return self.properties
    
    def get_name (self):
        return self.properties["name"]

    def get_provider (self):
        return self.provider

    def get_unread (self):
        return self.unread

    def get_new_unread (self):
        return self.new_unread

    def update (self):
        self.provider.update_account (self)
    
    def activate (self):
        print "Activated " , self.get_name()

