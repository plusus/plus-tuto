from time import sleep

from PySide.QtCore import Qt, QProcess, QEvent, QPoint, QTimer, QRect
from PySide.QtGui import QMainWindow, QRegion, QGraphicsScene, \
    QLabel, QIcon, QAction, QCloseEvent, QMoveEvent, \
    QShowEvent, QWidget, QApplication, QPalette
from pymouse import PyMouse

from plustutointerpreter.done_tutorial_saver import DoneTutorialSaver
from plustutointerpreter.thread.focus_thread import FocusThread
from plustutointerpreter.thread.shade_thread import ShadeThread
from plustutointerpreter.x11_helpers import poll_new_x_client, \
    close_window, send_mouse_event, minimize_window, get_top_parent, \
    get_window_object_from_id, unmaximize_window
from Xlib.display import Display
from threading import Timer

from Xlib.xobject.drawable import Window

from libtuto.zone import Zone
from libtuto.tutorial import TutorialStep
from libtuto.size import Size
from plustutointerpreter.utils import resource_filepath

from plustutointerpreter.overlay.overlay_graphics_item import \
    OverlayGraphicsItem
from plustutointerpreter.overlay.overlay_graphics_view import \
    OverlayGraphicsView
from plustutointerpreter.zone_controller import StepController
from plustutointerpreter.config_file_override import ConfigFileOverride


class OverlayWindow(QMainWindow):

    WINDOW_DECORATOR_OFFSET_Y = 78
    WINDOW_DECORATOR_OFFSET_X = 1
    STATUS_BAR_OFFSET = 12

    def __init__(self,
                 step_controller,
                 done_tutorial_saver,
                 process_name,
                 window_filter,
                 window_size,
                 config_file_override,
                 parent=None):
        """
        :param step_controller: Provides tutorial step instances for the
                                current context
        :type step_controller: StepController
        :param done_tutorial_saver: Saver used to indicate that the current
                                    tutorial was completed
        :type done_tutorial_saver: DoneTutorialSaver
        :param process_name: The process of the tutorial to start
        :type process_name: str
        :param window_filter: A substring of the title of the window to
                              control
        :type window_filter: str
        :type window_size: Size
        :type config_file_override: ConfigFileOverride
        :type parent: QWidget
        """
        super().__init__(parent)
        self._shade_thread = None
        """:type: ShadeThread"""
        self._focus_thread = None
        """:type: FocusThread"""
        self._step_controller = step_controller
        self._done_tutorial_saver = done_tutorial_saver
        self._mouse = PyMouse()
        self._config_file_override = config_file_override
        self.status_label = QLabel()
        """:type: QLabel"""
        self.process_name = process_name
        self.window_filter = window_filter
        self.window_controlled = None
        """:type: Window"""
        self.application_process = QProcess()
        self.display = Display()
        self._screen_geometry = QApplication.desktop().availableGeometry()
        """:type: QRect"""
        self.toolbar = self.addToolBar(self.trUtf8('Tutorial controls'))
        self.build_toolbar()
        self.first_time_shown = True
        self._fit_to_screen_timer = QTimer(self)
        """:type: QTimer"""
        self._fit_to_screen_timer.setSingleShot(True)
        self._fit_to_screen_timer.timeout.connect(self.fit_in_screen)

        self._init_window_attributes_and_flags()
        self._init_status_bar()

        self.start_control_application()
        unmaximize_window(self.display, self.window_controlled)

        scene = QGraphicsScene(self)
        self._graphicsView = OverlayGraphicsView(
            scene,
            self.handle_click)
        self._graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setCentralWidget(self._graphicsView)

        self._shade_overlay = OverlayGraphicsItem(
            lambda: step_controller.get_step(),
            lambda: step_controller.is_done())
        self.show_step_info(self._step_controller.get_step())
        scene.addItem(self._shade_overlay)
        self.shade()
        self._setup_size(window_size)

    def start_control_application(self):
        self.application_process.start(self.process_name)

        wid_to_embed = poll_new_x_client(self.window_filter,
                                         win_id_exclusion=self.winId())

        if wid_to_embed:
            self.window_controlled = get_window_object_from_id(self.display,
                                                               wid_to_embed)
        else:
            raise RuntimeError(self.trUtf8("Couldn't find the window to embed"))

    def closeEvent(self, event):
        """
        :type event: QCloseEvent
        """
        self._focus_thread.set_stop()
        while not self._focus_thread.isFinished():
            sleep(0.1)
        close_window(self.display, self.window_controlled)
        self.application_process.close()
        if self._config_file_override:
            self._config_file_override.restore_backed_up_files()

        super().closeEvent(event)

    def handle_click(self, point):
        """
        :type point: QPoint
        """
        if self._shade_thread is not None and self._shade_thread.isRunning():
            return

        clickable_region = self._compute_clickable_region(
            self._step_controller.get_step().actionZone)

        if clickable_region.contains(point):
            self.show_next_step()

    def shade(self):
        """
        :rtype: ShadeThread
        """
        self._shade_thread = ShadeThread(
            self._shade_overlay,
            self._graphicsView.update,
            lambda x: 0.001 * (x ** 3),
            lambda a: a < OverlayGraphicsItem.BACKGROUND_ALPHA,
            OverlayGraphicsItem.BACKGROUND_ALPHA)
        self._shade_thread.start()
        return self._shade_thread

    def unshade(self):
        """
        :rtype: ShadeThread
        """
        self._shade_thread = ShadeThread(
            self._shade_overlay,
            self._graphicsView.update,
            lambda x: OverlayGraphicsItem.BACKGROUND_ALPHA - (0.001 * (x ** 3)),
            lambda a: a > 0,
            0)
        self._shade_thread.start()
        return self._shade_thread

    def terminate(self, set_as_done=False):
        t = self.unshade()

        # noinspection PyUnresolvedReferences
        t.finished.connect(self.close)

        if set_as_done:
            self._done_tutorial_saver.save_as_done()

    def _compute_full_region(self):
        """
        :rtype: QRegion
        """
        size = self.size()
        """:type: QSize"""
        return QRegion(0, 0, size.width(), size.height())

    def _compute_clickable_region(self, zone):
        """
        Compute a hole region from a Zone instance
        :type zone: Zone
        :rtype: QRegion
        """
        top_left = zone.topLeft()
        bottom_right = zone.bottomRight()
        return QRegion(top_left[0],
                       top_left[1],
                       bottom_right[0] - top_left[0],
                       bottom_right[1] - top_left[1])

    def show_step_info(self, step):
        """
        :type step: TutorialStep
        """
        self.status_label.setText(step.title)

    def moveEvent(self, event):
        """
        :type event: QMoveEvent
        """
        super().moveEvent(event)
        if self.is_partially_offscreen():
            self._fit_to_screen_timer.start(200)
        self.window_controlled.configure(x=self.pos().x()+self.WINDOW_DECORATOR_OFFSET_X,
                                         y=self.pos().y()+self.WINDOW_DECORATOR_OFFSET_Y)

    def changeEvent(self, event):
        """
        :type event: QEvent
        """
        if event.type() == QEvent.Type.WindowStateChange:
            if self.windowState() == Qt.WindowMinimized:
                minimize_window(self.display, self.window_controlled)

    def build_toolbar(self):
        def on_step_action(fct):
            if not self._shade_thread.isRunning():
                fct()

        next_step_action = QAction(QIcon(resource_filepath('next_step.png')),
                                   self.trUtf8('Previous Step'), self)
        next_step_action.triggered.connect(
            lambda: on_step_action(self.show_next_step))

        previous_step_action = QAction(
            QIcon(resource_filepath('previous_step.png')),
            self.trUtf8('Next Step'), self)
        previous_step_action.triggered.connect(
            lambda: on_step_action(self.show_previous_step))

        self.toolbar.addAction(previous_step_action)
        self.toolbar.addAction(next_step_action)

    def refresh(self):
        self._graphicsView.repaint()
        self.show_step_info(self._step_controller.get_step())

    def show_next_step(self):
        action_zone_center = \
            self._step_controller.get_step().actionZone.center()

        send_mouse_event(self.display,
                         self.window_controlled,
                         *action_zone_center)
        try:
            self._step_controller.next()
        except StopIteration:
            self.terminate(set_as_done=True)
        self.refresh()

    def show_previous_step(self):
        previous_step_click = self._step_controller.get_step().previousStepClick

        if previous_step_click is not None:
            send_mouse_event(self.display,
                             self.window_controlled,
                             *previous_step_click.topLeft())

        if self._step_controller.has_previous():
            self._step_controller.previous()
        self.refresh()

    def showEvent(self, event):
        """
        :type event: QShowEvent
        """
        super().showEvent(event)
        if self.first_time_shown:
            Timer(0.5, self.start_focus_thread, ()).start()
            self.first_time_shown = False

    def start_focus_thread(self):
        x11_window = self.display.create_resource_object('window', self.winId())
        self._focus_thread = FocusThread(
            self.display,
            get_top_parent(self.display, x11_window),
            self.window_controlled)
        self._focus_thread.start()

    def _setup_size(self, window_size):
        """
        :type window_size: Size
        """
        self.setFixedSize(window_size.width() + self.WINDOW_DECORATOR_OFFSET_X,
                          window_size.height() + self.WINDOW_DECORATOR_OFFSET_Y \
                          - self.STATUS_BAR_OFFSET)
        self.window_controlled.configure(width=window_size.width(),
                                         height=window_size.height())
        self._shade_overlay.setSize(window_size.width(), window_size.height())

    def fit_in_screen(self):
        x = self.pos().x()
        y = self.pos().y()
        screen_width = self._screen_geometry.width()
        screen_height = self._screen_geometry.height()

        if screen_width < x + self.width():
            x = screen_width - self.width()
        elif x < 0:
            x = 0

        if screen_height - self.height() < y:
            y = screen_height - self.height() - self.STATUS_BAR_OFFSET
        elif y < 0:
            y = 0

        if x != self.pos().x() or y != self.pos().y():
            self.move(x, y)

    def is_partially_offscreen(self):
        x = self.pos().x()
        y = self.pos().y()
        return \
            self._screen_geometry.width() < x + self.width() or x < 0 or \
            self._screen_geometry.height() - self.height() < y or y < 0

    def _init_window_attributes_and_flags(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_X11DoNotAcceptFocus)
        self.setWindowFlags(self.windowFlags() & Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)

    def _init_status_bar(self):
        self.statusBar().addWidget(self.status_label)
        palette = QPalette()
        palette.setColor(QPalette.Background, Qt.lightGray)
        self.statusBar().setPalette(palette)