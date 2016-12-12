# plustuto
Tutorial software for the PLUS distribution

It is entirely written in Python 3 with PySide as toolkit

The application is made-up from two main software:
* plustutocenter: Center to consult tutorials and launch them
* plustutointerpreter: Interpreter of .tuto files which launches the application and displays an overlay on top of it allowing to execute it
* libtuto: Backend library which defines the standard tuto file format and loading in Python

## Prerequisites
Development packages
* python3.4
* python3-pyside
* pyside-tools
* qt4-designer
* qt4-dev-tools

Python libraries
* python3-xlib
* pyxdg
* ewmh
* PyInstaller (for standalone packaging)
* glob2 (for tests)

## To build as standalone
Run 'make' in:
* "center-frontend" to build dist of plustutocenter
* "core" to build dist of plustutointerpreter
* Root to build both

## Package build for Debian
./buildPackage.sh

> Note: All dependencies are included by PyInstaller, including PySide librairies. The built frontend and core are merged into a single directory which contains all necessary librairies for both, reducing the size compared to packaging them separately.

## Credits
Check/Cross icons: Designmodo (CC3: https://creativecommons.org/licenses/by/3.0/)
