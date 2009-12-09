import os
import sys
import urllib
import urllib2
import re
from gmailatom import GmailAtom
from greaderatom import GreaderAtom
import xdg.BaseDirectory as bd
import ConfigParser

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
	print g.sendRequest ().read()
	g.refreshInfo()
	return

def check_gmail ():
	g = GmailAtom (config.get ('gmail', 'username'), config.get ('gmail', 'password'))
	g.refreshInfo()
	
	if g.getUnreadMsgCount () > 0:
		#notificar ("GMail", 'Hay mensajes sin leer: ' + str (g.getUnreadMsgCount ()))
		message = ""
		for i in range (g.getUnreadMsgCount ()):
			message += "<b>Correo " + str(i+1) + "</b>: " + g.getMsgTitle (i) + "\n - \n"
		
		#notificar (g.getMsgTitle (i), g.getMsgSummary (i))
		notificar ("Cloud notifications", message)
	
	#print g.sendRequest().read()

def main ():
	global config
	
	if not os.path.exists (CONFIG_HOME):
		os.makedirs (CONFIG_HOME)

	if not os.path.exists (CONFIG_FILE):
		print 'El fichero de configuracion no existe: ' , CONFIG_FILE
		sys.exit (1)

	config = ConfigParser.ConfigParser()
	config.read (CONFIG_FILE)

	check_reader ()
	check_gmail ()

if __name__ == "__main__":
	main()


