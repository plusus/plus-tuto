import sys

from PySide.QtCore import QDir, QTranslator, Qt
from PySide.QtGui import QApplication, QMessageBox, QFileDialog
from os.path import join
from xdg.DesktopEntry import DesktopEntry

from libtuto.query_tutorials import loadTutorial, isValidTutoFile, \
    TutorialFileVersionMismatchException
from plustutointerpreter.config_file_override import ConfigFileOverride
from plustutointerpreter.done_tutorial_saver import DoneTutorialSaver
from plustutointerpreter.overlay.overlay_window import OverlayWindow
from plustutointerpreter.utils import project_root
from plustutointerpreter.zone_controller import StepController
from plustutointerpreter.x11_helpers import get_window_from_process_name
from Xlib.display import Display
from locale import getlocale, LC_MESSAGES


class App(QApplication):
    def __init__(self):
        super(App, self).__init__([])

        self.LOCALIZATION = getlocale(LC_MESSAGES)[0]
        translator = QTranslator(self)
        translator.load(join("i18n", "interpreter_" + self.LOCALIZATION),
                        project_root())
        self.installTranslator(translator)

        self.open_tuto = self.trUtf8("Open Tutorial")
        self.tuto_file_filter = self.trUtf8(".tuto file")
        self.close_windows = \
            self.trUtf8("Close all {} windows before running the tutorial")
        self.close_windows_title = \
            self.trUtf8("Target application already opened")

        self.field_missing_title = \
            self.trUtf8("Malformed tutorial file")
        self.field_missing = \
            self.trUtf8("The tutorial file is malformed "
                        "(field {} is missing). The file cannot be executed.")

        self.unsupported_file_title = \
            self.trUtf8("Unsupported file")
        self.unsupported_file = \
            self.trUtf8("The file version exceeds the supported version. "
                        "Consider updating the software to execute the file.")

APP = App()

# Check if argument is a valid tutorial file
tutoFile = sys.argv[1] if len(sys.argv) > 1 else ""
if not isValidTutoFile(tutoFile):
    # noinspection PyArgumentList
    tutoFile = QFileDialog.getOpenFileName(
        parent=None,
        caption=APP.open_tuto,
        dir=QDir.homePath(),
        filter=APP.tuto_file_filter + " (*.tuto)")[0]

if not isValidTutoFile(tutoFile):
    sys.exit()

tutorial = None
try:
    tutorial = loadTutorial(tutoFile, language=APP.LOCALIZATION)
except KeyError as e:
    msg_box = QMessageBox()
    msg_box.setWindowTitle(APP.field_missing_title)
    msg_box.setText(APP.field_missing.format(e))
    msg_box.show()
except TutorialFileVersionMismatchException as e:
    msg_box = QMessageBox()
    msg_box.setWindowTitle(APP.unsupported_file_title)
    msg_box.setText(APP.unsupported_file)
    msg_box.show()
if not tutorial:
    sys.exit(APP.exec_())

desktop_filepath = tutorial[0][0]
tuto_instance = tutorial[1]

window_filter = tuto_instance.windowTitleFilter
process_name = DesktopEntry(desktop_filepath).getExec().split()[0]

if get_window_from_process_name(Display(), process_name) is not None:
    msg_box = QMessageBox()
    msg_box.setWindowTitle(APP.close_windows_title)
    msg_box.setText(APP.close_windows.format(window_filter))
    msg_box.show()
else:
    config_file_override = None
    if tutorial[1].config_file_data:
        config_file_override = ConfigFileOverride(tuto_instance.config_file_data)

    overlay = OverlayWindow(StepController(tuto_instance.steps),
                            DoneTutorialSaver(tutoFile),
                            process_name,
                            window_filter,
                            tuto_instance.window_size,
                            config_file_override)
    overlay.setWindowTitle('Tutorial - {}'.format(tuto_instance.name))
    overlay.show()

APP.setAttribute(Qt.AA_X11InitThreads)
sys.exit(APP.exec_())
