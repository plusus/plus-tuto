from plustutocenter.controller.concretecontroller import ConcreteController
from plustutocenter.qt.view_qt import ViewQt


controller = ConcreteController()
controller.setView(ViewQt(controller))
controller.startApp()
