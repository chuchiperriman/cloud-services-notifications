class AccountData:

    unread = 0
    new_unread = 0
    
    def __init__ (self, name, provider):
        self.name = name
        self.provider = provider

    def get_name (self):
        return self.name

    def get_provider (self):
        return self.provider

    def get_unread (self):
        return self.unread

    def get_new_unread (self):
        return self.new_unread
