import gtk

def create_provider_widget(fields):
    table = gtk.Table(len(fields), 2)
    i = 0
    for f in fields:
        hbox = gtk.HBox()
        label = gtk.Label(f["label"])
        if f["type"] == "pwd":
            print 'password'
            entry = gtk.Entry()
            entry.set_visibility(False)
        else:
            entry = gtk.Entry()
            print 'string'
        table.attach(label, 0, 1, i, i+1)
        table.attach(entry, 1, 2, i, i+1)
        i += 1
    return table
