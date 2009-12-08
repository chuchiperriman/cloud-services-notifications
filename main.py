from gmailatom import GmailAtom
import xdg.BaseDirectory as bd
import ConfigParser

CONFIG_HOME = bd.xdg_config_home + '/servnotify'
CONFIG_FILE = CONFIG_HOME + '/configuration'

def notificar (title, message):
	try:
		import pynotify
		if pynotify.init("My Application Name"):
			n = pynotify.Notification(title, message)
			n.set_urgency(pynotify.URGENCY_LOW)
        		n.set_timeout (1000)
			n.show()
		else:
			print "there was a problem initializing the pynotify module"
	except:
		print "you don't seem to have pynotify installed"

cparser = ConfigParser.ConfigParser()
cparser.read (CONFIG_FILE)

g = GmailAtom (cparser.get ('gmail', 'username'), cparser.get ('gmail', 'password'))

g.refreshInfo()

if g.getUnreadMsgCount () > 0:
	#notificar ("GMail", 'Hay mensajes sin leer: ' + str (g.getUnreadMsgCount ()))
	for i in range (g.getUnreadMsgCount ()):
		notificar (g.getMsgTitle (i), g.getMsgSummary (i))
		pass;

#print g.sendRequest().read()
