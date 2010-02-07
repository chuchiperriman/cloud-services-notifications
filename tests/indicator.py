from time import time
import indicate
import gtk

server = indicate.indicate_server_ref_default()
server.set_type("message.im")
#server.connect("server-display", self.on_server_display_cb)
server.set_desktop_file("/usr/local/share/applications/cloudsn.desktop")
server.show()


inds = []

for i in range(10):
    indicator = indicate.Indicator()
    indicator.set_property("name", "Test account")
    indicator.set_property_time("time", time())
    indicator.set_property_int("count", 0)
    """
    if acc.get_provider().get_icon() is not None:
        indicator.set_property_icon("icon", acc.get_provider().get_icon())
    """ 
    indicator.show()
    inds.append(indicator)


#acc.indicator = indicator
#indicator.account = acc

#indicator.connect("user-display", self.on_indicator_display_cb)

gtk.main()
