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

get_oe ()
{
if [ -f /lib/libcrypto.so.1.0.0 ]
then
	oe="oe40"
else
	oe="oe16-30"
fi
echo  $oe
}


PLATFORM=$(get_platform)
OE=$(get_oe)
BASEDIR=$(dirname $0)
RTMPDIR="$BASEDIR/$PLATFORM/rtmp_$OE"
LIBDIR="/usr/lib"
BINDIR="/usr/bin"
GSTDIR="$LIBDIR/gstreamer-0.10/"

echo "RTMP plugin pre archivCZSK"
cp $RTMPDIR/librtmp.so $LIBDIR
cp $RTMPDIR/librtmp.so.0 $LIBDIR
cp $RTMPDIR/libgstrtmp.so $GSTDIR
cp $RTMPDIR/rtmpgw $BINDIR 2> /dev/null
cp $RTMPDIR/rtmpdump $BINDIR 2> /dev/null
chmod 755 $LIBDIR/librtmp*
chmod 755 $GSTDIR/libgstrtmp.so
chmod 755 $BINDIR/rtmp*
echo "RTMP plugin bol uspesne nainstalovany"
exit 0
