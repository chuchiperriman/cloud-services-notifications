import gnomekeyring as gkey


class GnomeKeyring(object):

    def __init__(self, name, server, protocol):
        self._name = name
        self._server = server
        self._protocol = protocol
        self._key = gkey.ITEM_NETWORK_PASSWORD
        self._keyring = gkey.get_default_keyring_sync()

    def has_credentials(self):
        try:

            if self._key == gkey.ITEM_NETWORK_PASSWORD:
                attrs = {"server": self._server, "protocol": self._protocol}
                items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
                return len(items) > 0
            if self._key == gkey.ITEM_GENERIC_SECRET:
                attrs = {"name": self._name}
                items = gkey.find_items_sync(gkey.ITEM_GENERIC_SECRET, attrs)
                return len(items) > 0
        except gkey.DeniedError:
            return False

    def get_credentials(self):
        attrs = {"server": self._server, "protocol": self._protocol}
        items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
        return (items[0].attributes["user"], items[0].secret)

    def remove_keyring(self, password):
        id = password.split(":")[1]
        gkey.item_delete_sync(self._keyring, int(id))

    def set_credentials(self, (user, pw)):
        attrs = {
            "user": user,
            "server": self._server,
            "protocol": self._protocol,
            }
        id = gkey.item_create_sync(gkey.get_default_keyring_sync(),\
             gkey.ITEM_NETWORK_PASSWORD, self._name, attrs, pw, True)
        return id
