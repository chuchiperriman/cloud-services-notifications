# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from gi.repository import Gtk

def create_provider_widget(fields):
    table = Gtk.Table(len(fields), 2)
    table.widgets = {}
    i = 0
    for f in fields:
        hbox = Gtk.HBox()
        label = Gtk.Label(f["label"])
        if f["type"] == "pwd":
            entry = Gtk.Entry()
            entry.set_visibility(False)
        elif f["type"] == "check":
            entry = Gtk.CheckButton()
        else:
            entry = Gtk.Entry()

        entry.set_name(f["label"])
        table.attach(label, 0, 1, i, i+1)
        table.attach(entry, 1, 2, i, i+1)
        i += 1
        table.widgets[f["label"]] = entry
    return table

def get_widget_by_label(table, label):
    return table.widgets[label]
