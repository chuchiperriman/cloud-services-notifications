# Based on invest-applet in gnome-applets


from cloudsn import logger
from dbus.mainloop.glib import DBusGMainLoop
import dbus

# possible states, see http://projects.gnome.org/NetworkManager/developers/api/09/spec.html#type-NM_STATE
STATE_UNKNOWN		= dbus.UInt32(0)
STATE_CONNECTED_GLOBAL = dbus.UInt32(70)

class NetworkManager:
	def __init__(self):
		self.state = STATE_UNKNOWN
		self.statechange_callback = None

		try:
			# get an event loop
			loop = DBusGMainLoop()

			# get the NetworkManager object from D-Bus
			logger.debug("Connecting to Network Manager via D-Bus")
			bus = dbus.SystemBus(mainloop=loop)
			nmobj = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
			nm = dbus.Interface(nmobj, 'org.freedesktop.NetworkManager')

			# connect the signal handler to the bus
			bus.add_signal_receiver(self.handler, None,
					'org.freedesktop.NetworkManager',
					'org.freedesktop.NetworkManager',
					'/org/freedesktop/NetworkManager')

			# get the current status of the network manager
			self.state = nm.state()
			logger.debug("Current Network Manager status is %d" % self.state)
		except Exception, msg:
			logger.error("Could not connect to the Network Manager: %s" % msg )

	def online(self):
		return self.state == STATE_UNKNOWN or self.state == STATE_CONNECTED_GLOBAL

	def offline(self):
		return not self.online()

	# the signal handler for signals from the network manager
	def handler(self,signal=None):
		if isinstance(signal, dict):
			state = signal.get('State')
			if state != None:
				logger.debug("Network Manager change state %d => %d" % (self.state, state) );
				self.state = state

				# notify about state change
				if self.statechange_callback != None:
					self.statechange_callback()

	def set_statechange_callback(self,handler):
		self.statechange_callback = handler
