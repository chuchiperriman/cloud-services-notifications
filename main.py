import os
import sys
import urllib
import urllib2
import re
from gmailatom import GmailAtom
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

	_cproc = urllib2.HTTPCookieProcessor()
	opener = urllib2.build_opener(_cproc)
	urllib2.install_opener(opener)
	login_url = "https://www.google.com/accounts/ServiceLogin"
	auth_url = "https://www.google.com/accounts/ServiceLoginAuth"
	
	f = urllib2.urlopen(login_url)
	data = f.read()
	galx_match_obj = re.search(r'name="GALX"\s*value="([^"]+)"', data, re.IGNORECASE)
	galx_value = galx_match_obj.group(1) if galx_match_obj.group(1) is not None else ''
	params = urllib.urlencode({'Email':config.get ('gmail', 'username'),
				'Passwd':config.get ('gmail', 'password'),
				'GALX':galx_value})
		   
        f = urllib2.urlopen(auth_url, params)

	f = opener.open('https://www.google.com/reader/api/0/unread-count')

	data = f.read()
	print data

def check_gmail ():
	g = GmailAtom (config.get ('gmail', 'username'), config.get ('gmail', 'password'))
	g.refreshInfo()
	
	if g.getUnreadMsgCount () > 0:
		#notificar ("GMail", 'Hay mensajes sin leer: ' + str (g.getUnreadMsgCount ()))
		for i in range (g.getUnreadMsgCount ()):
			notificar (g.getMsgTitle (i), g.getMsgSummary (i))

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

"""
g = GmailAtom (cparser.get ('gmail', 'username'), cparser.get ('gmail', 'password'))

g.refreshInfo()

if g.getUnreadMsgCount () > 0:
	#notificar ("GMail", 'Hay mensajes sin leer: ' + str (g.getUnreadMsgCount ()))
	for i in range (g.getUnreadMsgCount ()):
		notificar (g.getMsgTitle (i), g.getMsgSummary (i))
		pass;

#print g.sendRequest().read()
"""

if __name__ == "__main__":
	main()


