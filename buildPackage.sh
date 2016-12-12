#!/bin/bash -e

PACKAGE_NAME=plustuto
VERSION_MAJOR=1
VERSION_MINOR=1
VERSION_BUILD=1
VERSION="$VERSION_MAJOR.$VERSION_MINOR-$VERSION_BUILD"
SEP="_"
PACKAGE_NAME_VERSION=$PACKAGE_NAME$SEP$VERSION
ARCHITECTURE=`dpkg --print-architecture`
PACKAGE_DIR=builddeb/$PACKAGE_NAME_VERSION

rm -rf builddeb/$PACKAGE_NAME_VERSION

echo '### BUILDING STANDALONE BINARIES'
mkdir -p $PACKAGE_DIR/opt/plustuto
mkdir -p $PACKAGE_DIR/usr/bin
# Make project and copy dist to plustuto folder
make
rsync -a center-frontend/dist/plustutocenter/ $PACKAGE_DIR/opt/plustuto/
rsync -a core/dist/plustutointerpreter/ $PACKAGE_DIR/opt/plustuto/

# Copy symlinks to /usr/bin
ln -sf /opt/plustuto/plustutocenter $PACKAGE_DIR/usr/bin/
ln -sf /opt/plustuto/plustutointerpreter $PACKAGE_DIR/usr/bin/

# Copy icon files
ICON_DIR=$PACKAGE_DIR/usr/share/icons/hicolor/scalable
mkdir -p $ICON_DIR/apps
cp icons/plustutocenter.svg $ICON_DIR/apps/
cp icons/plustutointerpreter.svg $ICON_DIR/apps/
mkdir -p $ICON_DIR/mimetypes
cp icons/application-libtuto.svg $ICON_DIR/mimetypes/

# Copy mimetype descriptor
mkdir -p $PACKAGE_DIR/usr/share/mime/packages
cp mime/libtuto.xml $PACKAGE_DIR/usr/share/mime/packages/

# Copy desktop files
mkdir -p $PACKAGE_DIR/usr/share/applications
cp -f desktopfiles/* $PACKAGE_DIR/usr/share/applications/

# Copy debian base files
mkdir -p $PACKAGE_DIR/DEBIAN
rsync -a debian/ $PACKAGE_DIR/DEBIAN/

# Copy libtuto to python2 dist-packages
mkdir -p $PACKAGE_DIR/usr/lib/python2.7/dist-packages/libtuto
rm -rf tuto-file-handling/libtuto/__pycache__
cp -rf tuto-file-handling/libtuto/* $PACKAGE_DIR/usr/lib/python2.7/dist-packages/libtuto/
# Symlink to python3 dist-packages
mkdir -p $PACKAGE_DIR/usr/lib/python3/dist-packages
ln -sf /usr/lib/python2.7/dist-packages/libtuto $PACKAGE_DIR/usr/lib/python3/dist-packages/libtuto

# Copy default config files
mkdir -p $PACKAGE_DIR/usr/share/libtuto/
cp -r default_config/ $PACKAGE_DIR/usr/share/libtuto/

cd builddeb/$PACKAGE_NAME_VERSION

echo '### CREATING CONTROL FILE'
mkdir -p DEBIAN
CONTROL_FILE="DEBIAN/control"
touch DEBIAN/control
echo "Package: ${PACKAGE_NAME}" > "$CONTROL_FILE"
echo "Version: $VERSION" >> "$CONTROL_FILE"
echo "Section: misc" >> "$CONTROL_FILE"
echo "Priority: optional" >> "$CONTROL_FILE"
echo "Architecture: $ARCHITECTURE" >> "$CONTROL_FILE"
echo "Essential: no" >> "$CONTROL_FILE"
echo "Installed-Size: `du -sc opt usr | grep total | awk '{ print $1 }'`" >> "$CONTROL_FILE"
echo "Maintainer: Samuel Longchamps <samuel.longchamps@usherbrooke.ca>" >> "$CONTROL_FILE"
echo "Homepage: http://plus-us.gel.usherbrooke.ca/plustuto" >> "$CONTROL_FILE"
echo "Description: PLUS tutorial application and interpreter" >> "$CONTROL_FILE"
echo " Allows to consult .tuto files as interactive tutorials." >> "$CONTROL_FILE"

# Create md5sum
find . -type f ! -regex '.*.hg.*' ! -regex '.*?debian-binary.*' ! -regex '.*?DEBIAN.*' -printf '"%P" ' | xargs md5sum > DEBIAN/md5sums

cd ..

dpkg-deb -bv $PACKAGE_NAME_VERSION $PACKAGE_NAME_VERSION"_"$ARCHITECTURE".deb"
