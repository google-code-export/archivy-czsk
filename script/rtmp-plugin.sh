#!/bin/sh

get_platform ()
{
local platform=$(uname -m)

if [ "$platform" == "sh4" ]
then
	platform="sh4"
else
	platform="mipsel"
fi
echo $platform
}

PLATFORM=$(get_platform)
BASEDIR=$(dirname $0)
RTMPDIR="$BASEDIR/$PLATFORM/rtmp"
LIBDIR="/usr/lib"
GSTDIR="$LIBDIR/gstreamer-0.10/"

echo "RTMP plugin pre archivCZSK"
cp $RTMPDIR/librtmp.so $LIBDIR
cp $RTMPDIR/librtmp.so.0 $LIBDIR
cp $RTMPDIR/libgstrtmp.so $GSTDIR
chmod 755 $LIBDIR/librtmp*
chmod 755 $GSTDIR/libgstrtmp.so
echo "RTMP plugin bol uspesne nainstalovany"
exit 0
