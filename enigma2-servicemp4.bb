DESCRIPTION = "Servicemp4 for more streaming options, based on servicemp3 from Openpli "
MAINTAINER = "mx3L <mxfitsat@gmail.com>"
HOMEPAGE = "http://code.google.com/servicemp4/"
LICENSE = "GNU GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=d41d8cd98f00b204e9800998ecf8427e"
SECTION = "extra"

PN="enigma2-plugin-extensions-servicemp4"

PV="0.1"
PR = "r0"

SRC_URI = "file://${FILE_DIRNAME}/build"
S = "${WORKDIR}/build"

EXTRA_OECONF = " \
        BUILD_SYS=${BUILD_SYS} \
        HOST_SYS=${HOST_SYS} \
        STAGING_INCDIR=${STAGING_INCDIR} \
        STAGING_LIBDIR=${STAGING_LIBDIR} \
"

FILES_${PN} += " /usr/lib/enigma2/python/Plugins/Extensions/Servicemp4"

FILES_${PN}-dbg = " /usr/lib/enigma2/python/Plugins/Extensions/Servicemp4/.debug "

DEPENDS = "enigma2"

inherit autotools
