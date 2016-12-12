#!/usr/bin/env bash

PRO_FILE=plustutointerpreter.pro
PY_FILES=$(find . -iregex '.**\.py' -printf '%p ')
UI_FILES=$(find . -iregex '.**\.ui' -printf '%p ')

echo > $PRO_FILE
echo SOURCES = $PY_FILES >> $PRO_FILE
echo FORMS = $UI_FILES >> $PRO_FILE
echo TRANSLATIONS = i18n/interpreter_fr_CA.ts >> $PRO_FILE


mkdir i18n -p
pyside-lupdate $PRO_FILE
