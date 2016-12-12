from time import sleep

from PySide.QtCore import QThread
from PySide.QtGui import QWidget
from Xlib import X
from Xlib.display import Display
from Xlib.xobject.drawable import Window

from plustutointerpreter.x11_helpers import get_stacking_index, raise_window


class FocusThread(QThread):
    def __init__(self, display,
                 master,
                 slave,
                 parent=None):
        """
        :type display: Display
        :type master: Window
        :type slave: Window
        :type parent: QWidget
        """
        super().__init__(parent)
        self.display = display
        self.display.screen().root.change_attributes(
            event_mask=X.SubstructureNotifyMask)
        self.master = master
        self.slave = slave
        self.isRunning = False

    def run(self):
        self.isRunning = True
        self._synchronize(self.slave)

        while self.isRunning:
            sleep(1.0 / 60.0)

            if self.display.pending_events() > 0:
                event = self.display.next_event()

                # The X11 event ConfigureNotify is received when Z Order of the
                # windows has changed.
                if event.type == X.ConfigureNotify:
                    self._synchronize(event.window)

    def set_stop(self):
        self.isRunning = False

    def _synchronize(self, event_window):
        # Find the Z Order of the two windows
        slave_stack_index = get_stacking_index(self.display, self.slave)
        master_stack_index = get_stacking_index(self.display, self.master)

        if slave_stack_index is not None and master_stack_index is not None:
            # Check for desynchronization of the window based on the Z Order
            if event_window == self.slave and slave_stack_index > master_stack_index:
                raise_window(self.display,
                             self.master.query_tree().children[0])
            elif event_window == self.master and \
                    slave_stack_index != master_stack_index - 1:
                raise_window(self.display, self.slave)
