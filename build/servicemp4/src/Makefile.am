SYSROOT_DIR=/media/a2e14f15-a75e-44e9-907c-8a005813e1cb_/openplimipsel/openpli-oe-core/build-et6x00/tmp/sysroots/et6x00/usr/include

#AM_CPPFLAGS = \
#	-I$(SYSROOT_DIR)/gstreamer-0.10 \
#        -I$(SYSROOT_DIR)/glib-2.0 \
#        -I$(SYSROOT_DIR)/glib-2.0/include
#
plugindir = $(libdir)/enigma2/python/Plugins/Extensions/Servicemp4
plugin_LTLIBRARIES = servicemp4.la

servicemp4_la_SOURCES = \
servicemp4.cpp \
servicemp4.h

servicemp4_la_LDFLAGS = \
-avoid-version -module -shared
