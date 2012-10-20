# -*- mode: python; tab-width: 4; indent-tabs-mode: nil -*-
from cloudsn.core.provider import Provider, ProviderManager
from cloudsn.core import account, config, networkmanager, notification, utils, indicator
from cloudsn.ui import window
from cloudsn import logger
from cloudsn.ui.authwarning import check_auth_configuration
from time import time
from gi.repository import Gtk, GObject
import gettext
import thread

class Controller (GObject.Object):

    __default = None

    __gtype_name__ = "Controller"

    __gsignals__ = { "account-checked" : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
                     "account-check-error" : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))}

    timeout_id = -1
    interval = 60

    def __init__(self):
        if Controller.__default:
           raise Controller.__default

        #Prevent various instances
        GObject.Object.__init__(self)
        import os, fcntl, sys, tempfile, getpass
        self.lockfile = os.path.normpath(tempfile.gettempdir() + '/cloudsn-'+getpass.getuser()+'.lock')
        self.fp = open(self.lockfile, 'w')
        try:
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            message = _("Another instance is already running, close it first.")
            logger.warn (message)
            print message.encode('utf-8')
            raise Exception (message)

        self.started = False
        self.config = config.SettingsController.get_instance()
        self.config.connect("value-changed", self._settings_changed)
        self.prov_manager = ProviderManager.get_instance()
        self.im = indicator.IndicatorManager.get_instance()
        self.am = account.AccountManager.get_instance()
        self.am.connect("account-added", self._account_added_cb)
        self.am.connect("account-deleted", self._account_deleted_cb)
        self.am.connect("account-changed", self._account_changed_cb)
        self.am.connect("account-active-changed", self._account_active_cb)
        self.am.load_accounts()
        self.accounts_checking = []
        self.nm = networkmanager.NetworkManager()

    @staticmethod
    def get_instance():
        if not Controller.__default:
            Controller.__default = Controller()
        return Controller.__default

    def _account_added_cb(self, am, acc):
        indi = self.im.get_indicator()
        if indi and acc.get_active():
            indi.create_indicator(acc)

        if self.started:
            self.update_account(acc)

    def _account_deleted_cb(self, am, acc):
        self.im.get_indicator().remove_indicator(acc)

    def _account_active_cb(self, am, acc):
        if acc.get_active():
            self.im.get_indicator().create_indicator(acc)
            self.update_account(acc)
        else:
            self.im.get_indicator().remove_indicator(acc)

    def _account_changed_cb (self, am, acc):
        self.update_account(acc)

    def _settings_changed(self, config, section, key, value):
        if section == "preferences" and key == "minutes":
            self._update_interval()

    def _update_interval(self):
        old = self.interval
        self.interval = int(float(self.config.get_prefs()["minutes"]) * 60)

        if not self.get_active():
            return

        if self.timeout_id < 0:
            logger.debug("new source: "+str(self.timeout_id))
            self.timeout_id = GObject.timeout_add_seconds(self.interval,
                                self.update_accounts, None)
        elif self.interval != old:
            logger.debug("removed source: "+str(self.timeout_id))
            GObject.source_remove(self.timeout_id)
            logger.debug("restart source: "+str(self.timeout_id))
            self.timeout_id = GObject.timeout_add_seconds(self.interval,
                                self.update_accounts, None)

    def on_nm_state_changed (self):
        if self.nm.state == networkmanager.STATE_CONNECTED:
            logger.debug("Network connected")
            #Force update
            self.update_accounts()
        else:
            logger.debug("Network disconnected")

    def set_active(self, active):
        if active and not self.get_active():
            self.timeout_id = GObject.timeout_add_seconds(self.interval,
                                self.update_accounts, None)
            logger.debug("activated source: "+str(self.timeout_id))
        elif not active and self.get_active():
            GObject.source_remove(self.timeout_id)
            logger.debug("deactivated source "+str(self.timeout_id))
            self.timeout_id = -1


    def get_active(self):
        return self.timeout_id > -1

    def update_account(self, acc):
        if not self.get_active():
            return
        """acc=None will check all accounts"""
        if self.nm.offline():
            logger.warn ("The network is not connected, the account cannot be updated")
            return

        #TODO Check if the updater is running
        if acc is None:
            for acc in self.am.get_accounts():
                thread.start_new_thread(self.__real_update_account, (acc,))
        else:
            thread.start_new_thread(self.__real_update_account, (acc,))

        #self.__real_update_account(acc)

    def __real_update_account(self, acc):
        if acc in self.accounts_checking:
            logger.warn("The account %s is being checked" % (acc.get_name()))
            return

        logger.debug("Starting checker")
        if not acc.get_active():
            logger.debug("The account %s is not active, it will not be updated" % (acc.get_name()))
            return

        self.accounts_checking.append(acc)
        max_notifications = int(float(self.config.get_prefs()["max_notifications"]))
        try:
            logger.debug('Updating account: ' + acc.get_name())

            #Process events to show the main icon
            while Gtk.events_pending():
                Gtk.main_iteration(False)

            self.am.update_account(acc)

            acc.error_notified = False

            if hasattr(acc, "indicator"):
                self.im.get_indicator().update_account(acc)


            #Process events to show the indicator menu
            while Gtk.events_pending():
                Gtk.main_iteration(False)

            if acc.get_provider().has_notifications() and \
                    acc.get_show_notifications():
                nots = acc.get_new_unread_notifications()
                message = None
                if len(nots) > max_notifications:
                    notification.notify(acc.get_name(),
                        _("New messages: ") + str(len(nots)),
                        acc.get_icon())

                if len(nots) > 0 and len(nots) <= max_notifications:
                    for n in nots:
                        if n.icon:
                            icon = n.icon
                        else:
                            icon = acc.get_icon()
                        notification.notify(acc.get_name() + ": " + n.sender,
                            n.message,
                            icon)

            self.emit("account-checked", acc)
        except notification.NotificationError, ne:
            logger.exception("Error trying to notify with libnotify: %s", e)
        except Exception, e:
            logger.exception("Error trying to update the account %s: %s", acc.get_name(), e)
            if not acc.error_notified:
                acc.error_notified = True
                notification.notify (_("Error checking account %s") % (acc.get_name()),
                    str(e),
                    acc.get_icon())
                self.im.get_indicator().update_error(acc)
            self.emit("account-check-error", acc)
        finally:
            self.accounts_checking.remove(acc)

        logger.debug("Ending checker")

    def update_accounts(self, data=None):
        if not self.get_active():
            return True
        self.update_account(None)
        #For the timeout_add_seconds
        return True

    def _start_idle(self):
        try:
            check_auth_configuration()
            self.nm.set_statechange_callback(self.on_nm_state_changed)
            self.set_active (True)
            self.update_accounts()
            self.started = True
            #if len(self.am.get_accounts()) == 0:
            win = window.MainWindow.get_instance()
            win.run()
        except Exception, e:
            logger.exception ("Error starting the application: %s", e)
            try:
                notification.notify(_("Application Error"),
                    _("Error starting the application: %s") % (str(e)),
                    utils.get_error_pixbuf())
            except Exception, e:
                logger.exception ("Error notifying the error: %s", e)

        return False

    def start(self):
        GObject.threads_init()
        GObject.idle_add(self._start_idle)
        try:
            Gtk.main()
        except KeyboardInterrupt:
            logger.info ('KeyboardInterrupt the main loop')

