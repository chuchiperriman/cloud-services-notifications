#!/usr/bin/python
import os
import sys
import urllib
import urllib2
import re
from gmailatom import GmailAtom
from greaderatom import GreaderAtom
import xdg.BaseDirectory as bd
import ConfigParser
import indicate
from time import time
import gobject
import gtk

CONFIG_HOME = bd.xdg_config_home + '/cloud-services-notifications'
CONFIG_FILE = CONFIG_HOME + '/configuration'

def notificar (title, message):
	try:
		import pynotify
		if pynotify.init("My Application Name"):
			n = pynotify.Notification(title, message)
			n.set_urgency(pynotify.URGENCY_LOW)
			n.show()
		else:
			print "there was a problem initializing the pynotify module"
	except:
		print "you don't seem to have pynotify installed"

def check_reader ():

	g = GreaderAtom (config.get ('gmail', 'username'), config.get ('gmail', 'password'))
	g.refreshInfo()
	
	if g.getTotalUnread() > 0:
		notificar ("Google Reader", "Unread feeds: " + str(g.getTotalUnread ()))


def check_gmail ():
	g = GmailAtom (config.get ('gmail', 'username'), config.get ('gmail', 'password'))
	g.refreshInfo()
	
	if g.getUnreadMsgCount () > 0:
		message = ""
		for i in range (g.getUnreadMsgCount ()):
			message += "- \n" + g.getMsgTitle (i) + "\n"
		
		notificar ("GMail (" + str(g.getUnreadMsgCount ()) + ")", message)


test_count = 0
def timeout_cb(indicator):
	global test_count
	test_count +=1
	print "Modifying properties"
	#indicator.set_property_time("time", time())
	indicator.set_property_int("count", test_count)
	#indicator.set_property_icon("icon", pixbuf)
	
	if test_count > 2:
		gtk.main_quit()
		return False
	return True

def display(indicator):
	print "Ah, my indicator has been displayed"
    
def server_display(server):
	print "Ah, my server has been displayed"
    
def install_indicator():
	server = indicate.indicate_server_ref_default()
	server.set_type("message.im")
	server.set_desktop_file("/home/perriman/dev/cloud-services-notifications/cloudsn.desktop")
	server.connect("server-display", server_display)

	indicator = indicate.Indicator()
	indicator.set_property("name", "Test Account")
	indicator.set_property_time("time", time())
	indicator.set_property_int("count", test_count)
	indicator.show()

	indicator.connect("user-display", display)

	gobject.timeout_add_seconds(5, timeout_cb, indicator)
	
	#Sin el gtk.main() no funciona
	gtk.main()

def main ():
	global config
	
	if not os.path.exists (CONFIG_HOME):
		os.makedirs (CONFIG_HOME)

	if not os.path.exists (CONFIG_FILE):
		print 'El fichero de configuracion no existe: ' , CONFIG_FILE
		sys.exit (1)

	config = ConfigParser.ConfigParser()
	config.read (CONFIG_FILE)

	install_indicator ()
	check_reader ()
	check_gmail ()

if __name__ == "__main__":
	main()


