import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop


DBusGMainLoop(set_as_default=True)

LIBTUTO_DBUS_INTERFACE = 'ca.plusus.plustuto.persistence'
LIBTUTO_DBUS_PATH = '/ca/plusus/plustuto/persistence'


class LibtutoDbusHandler(dbus.service.Object):
    """
    Class which is used to
    """
    def __init__(self):
        bus_name = dbus.service.BusName(LIBTUTO_DBUS_INTERFACE,
                                        bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name,
                                     LIBTUTO_DBUS_PATH)

    @dbus.service.signal(LIBTUTO_DBUS_INTERFACE)
    def update_tuto_num(self):
        pass

LIBTUTO_DBUS_HANDLER = None


def tutorials_todo_update():
    """
    Update through DBus the service showing the number of tutorials to do
    """
    global LIBTUTO_DBUS_HANDLER
    if LIBTUTO_DBUS_HANDLER is None:
        LIBTUTO_DBUS_HANDLER = LibtutoDbusHandler()

    LIBTUTO_DBUS_HANDLER.update_tuto_num()


def register_todo_update(callback):
    """
    Register a callback to be called when the number of tutorials changes
    """
    dbus.SessionBus().add_signal_receiver(
        callback, "update_tuto_num", LIBTUTO_DBUS_INTERFACE, None, None)
