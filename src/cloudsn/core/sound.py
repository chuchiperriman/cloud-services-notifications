# -*- coding: UTF8 -*-

# Based on:
# Specto , Unobtrusive event notifier
#
#       sound.py
#

from cloudsn import logger
from cloudsn.core import config, utils

#TODO If we import the modules but the sound is disabled, we load
#arround 1,5mb of memory

enabled = False
try:
    #TODO Disabled because I need study how to do it with gtk-3 
    raise Exception("Sound is unsuported by the moment")
    import pygst
    pygst.require("0.10")
    import gst
    enabled = True
except Exception, e:
    logger.warn("Cloudsn cannot play sounds because pygst >= 0.10 is not installed")

class Sound:
    def __init__(self):
        self.player = None
        self.playing = False

    def play(self, uri):
        global enabled
        if not enabled:
            return

        if not utils.get_boolean(config.SettingsController.get_instance().get_prefs()["enable_sounds"]):
            return

        if uri and self.playing == False:
            self.player = gst.element_factory_make("playbin", "player")
            uri =  "file://" + uri
            self.player.set_property('uri', uri)
            bus = self.player.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)

            self.player.set_state(gst.STATE_PLAYING)
            self.playing = True

    def on_message(self, bus, message):
        #remove the pipeline is the sound is finished playing
        # and allow new sounds to be played from specto
        if message.type == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.playing = False

