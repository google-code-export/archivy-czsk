	/* note: this requires gstreamer 0.10.x and a big list of plugins. */
	/* it's currently hardcoded to use a big-endian alsasink as sink. */
#include <lib/base/ebase.h>
#include <lib/base/eerror.h>
#include <lib/base/init_num.h>
#include <lib/base/init.h>
#include <lib/base/nconfig.h>
#include <lib/base/object.h>
#include <lib/dvb/decoder.h>
#include <lib/components/file_eraser.h>
#include <lib/gui/esubtitle.h>
#include "servicemp4.h"
#include <lib/service/service.h>
#include <lib/gdi/gpixmap.h>

#include <string>

#include <gst/gst.h>
#include <gst/pbutils/missing-plugins.h>
#include <sys/stat.h>

typedef enum
{
	GST_PLAY_FLAG_VIDEO         = 0x00000001,
	GST_PLAY_FLAG_AUDIO         = 0x00000002,
	GST_PLAY_FLAG_TEXT          = 0x00000004,
	GST_PLAY_FLAG_VIS           = 0x00000008,
	GST_PLAY_FLAG_SOFT_VOLUME   = 0x00000010,
	GST_PLAY_FLAG_NATIVE_AUDIO  = 0x00000020,
	GST_PLAY_FLAG_NATIVE_VIDEO  = 0x00000040,
	GST_PLAY_FLAG_DOWNLOAD      = 0x00000080,
	GST_PLAY_FLAG_BUFFERING     = 0x000000100
} GstPlayFlags;

// eServiceFactoryMP4

/*
 * gstreamer suffers from a bug causing sparse streams to loose sync, after pause/resume / skip
 * see: https://bugzilla.gnome.org/show_bug.cgi?id=619434
 * As a workaround, we run the subsink in sync=false mode
 */

#define GSTREAMER_SUBTITLE_SYNC_MODE_BUG
/**/

eServiceFactoryMP4::eServiceFactoryMP4()
{
	ePtr<eServiceCenter> sc;

	eServiceCenter::getPrivInstance(sc);
	if (sc)
	{
		std::list<std::string> extensions;
		extensions.push_back("dts");
		extensions.push_back("mp2");
		extensions.push_back("mp3");
		extensions.push_back("ogg");
		extensions.push_back("mpg");
		extensions.push_back("vob");
		extensions.push_back("wav");
		extensions.push_back("wave");
		extensions.push_back("m4v");
		extensions.push_back("mkv");
		extensions.push_back("avi");
		extensions.push_back("divx");
		extensions.push_back("dat");
		extensions.push_back("flac");
		extensions.push_back("flv");
		extensions.push_back("mp4");
		extensions.push_back("mov");
		extensions.push_back("m4a");
		extensions.push_back("3gp");
		extensions.push_back("3g2");
		extensions.push_back("asf");
		extensions.push_back("wmv");
		extensions.push_back("wma");
		sc->addServiceFactory(eServiceFactoryMP4::id, this, extensions);
	}

	m_service_info = new eStaticServiceMP4Info();
}

eServiceFactoryMP4::~eServiceFactoryMP4()
{
	ePtr<eServiceCenter> sc;

	eServiceCenter::getPrivInstance(sc);
	if (sc)
		sc->removeServiceFactory(eServiceFactoryMP4::id);
}

DEFINE_REF(eServiceFactoryMP4)

	// iServiceHandler
RESULT eServiceFactoryMP4::play(const eServiceReference &ref, ePtr<iPlayableService> &ptr)
{
		// check resources...
	ptr = new eServiceMP4(ref);
	return 0;
}

RESULT eServiceFactoryMP4::record(const eServiceReference &ref, ePtr<iRecordableService> &ptr)
{
	ptr=0;
	return -1;
}

RESULT eServiceFactoryMP4::list(const eServiceReference &, ePtr<iListableService> &ptr)
{
	ptr=0;
	return -1;
}

RESULT eServiceFactoryMP4::info(const eServiceReference &ref, ePtr<iStaticServiceInformation> &ptr)
{
	ptr = m_service_info;
	return 0;
}

class eMP4ServiceOfflineOperations: public iServiceOfflineOperations
{
	DECLARE_REF(eMP4ServiceOfflineOperations);
	eServiceReference m_ref;
public:
	eMP4ServiceOfflineOperations(const eServiceReference &ref);

	RESULT deleteFromDisk(int simulate);
	RESULT getListOfFilenames(std::list<std::string> &);
	RESULT reindex();
};

DEFINE_REF(eMP4ServiceOfflineOperations);

eMP4ServiceOfflineOperations::eMP4ServiceOfflineOperations(const eServiceReference &ref): m_ref((const eServiceReference&)ref)
{
}

RESULT eMP4ServiceOfflineOperations::deleteFromDisk(int simulate)
{
	if (!simulate)
	{
		std::list<std::string> res;
		if (getListOfFilenames(res))
			return -1;

		eBackgroundFileEraser *eraser = eBackgroundFileEraser::getInstance();
		if (!eraser)
			eDebug("FATAL !! can't get background file eraser");

		for (std::list<std::string>::iterator i(res.begin()); i != res.end(); ++i)
		{
			eDebug("Removing %s...", i->c_str());
			if (eraser)
				eraser->erase(i->c_str());
			else
				::unlink(i->c_str());
		}
	}
	return 0;
}

RESULT eMP4ServiceOfflineOperations::getListOfFilenames(std::list<std::string> &res)
{
	res.clear();
	res.push_back(m_ref.path);
	return 0;
}

RESULT eMP4ServiceOfflineOperations::reindex()
{
	return -1;
}


RESULT eServiceFactoryMP4::offlineOperations(const eServiceReference &ref, ePtr<iServiceOfflineOperations> &ptr)
{
	ptr = new eMP4ServiceOfflineOperations(ref);
	return 0;
}

// eStaticServiceMP4Info


// eStaticServiceMP4Info is seperated from eServiceMP4 to give information
// about unopened files.

// probably eServiceMP4 should use this class as well, and eStaticServiceMP4Info
// should have a database backend where ID3-files etc. are cached.
// this would allow listing the mp3 database based on certain filters.

DEFINE_REF(eStaticServiceMP4Info)

eStaticServiceMP4Info::eStaticServiceMP4Info()
{
}

RESULT eStaticServiceMP4Info::getName(const eServiceReference &ref, std::string &name)
{
	if ( ref.name.length() )
		name = ref.name;
	else
	{
		size_t last = ref.path.rfind('/');
		if (last != std::string::npos)
			name = ref.path.substr(last+1);
		else
			name = ref.path;
	}
	return 0;
}

int eStaticServiceMP4Info::getLength(const eServiceReference &ref)
{
	return -1;
}

int eStaticServiceMP4Info::getInfo(const eServiceReference &ref, int w)
{
	switch (w)
	{
	case iServiceInformation::sTimeCreate:
		{
			struct stat s;
			if(stat(ref.path.c_str(), &s) == 0)
			{
				return s.st_mtime;
			}
		}
		break;
	}
	return iServiceInformation::resNA;
}

PyObject* eStaticServiceMP4Info::getInfoObject(const eServiceReference &ref, int w)
{
	switch(w)
	{
	case iServiceInformation::sFileSize:
		{
			struct stat s;
			if(stat(ref.path.c_str(), &s) == 0)
			{
				return PyLong_FromLongLong(s.st_size);
			}
		}
		break;
	}
	Py_RETURN_NONE;
}

// eServiceMP4
int eServiceMP4::ac3_delay = 0,
    eServiceMP4::pcm_delay = 0;

eServiceMP4::eServiceMP4(eServiceReference ref)
	:m_ref(ref), m_pump(eApp, 1)
{
	m_subtitle_sync_timer = eTimer::create(eApp);
	m_streamingsrc_timeout = 0;
	m_stream_tags = 0;
	m_currentAudioStream = -1;
	m_currentSubtitleStream = -1;
	m_cachedSubtitleStream = 0; /* report the first subtitle stream to be 'cached'. TODO: use an actual cache. */
	m_subtitle_widget = 0;
	m_currentTrickRatio = 1.0;
	m_buffer_duration = 5;
	m_buffer_size = 5 * 1024 * 1024;
	m_download_buffer_size =  (guint64)(8LL * 1024LL * 1024LL);
	m_http_timeout = 20;
	m_ignore_buffering_messages = 0;
	m_is_live = false;
	m_use_prefillbuffer = false;
	m_download_mode = false;
	m_download_path = "";
	m_download_buffer_path = "";
	m_prev_decoder_time = -1;
	m_decoder_time_valid_state = 0;
	m_errorInfo.missing_codec = "";
	audioSink = videoSink = NULL;

	CONNECT(m_subtitle_sync_timer->timeout, eServiceMP4::pushSubtitles);
	CONNECT(m_pump.recv_msg, eServiceMP4::gstPoll);
	m_aspect = m_width = m_height = m_framerate = m_progressive = -1;

	m_state = stIdle;
	eDebug("eServiceMP4::construct!");

	const char *filename = m_ref.path.c_str();
	const char *ext = strrchr(filename, '.');
	if (!ext)
		ext = filename + strlen(filename);

	m_sourceinfo.is_video = FALSE;
	m_sourceinfo.audiotype = atUnknown;
	if ( (strcasecmp(ext, ".mpeg") && strcasecmp(ext, ".mpg") && strcasecmp(ext, ".vob") && strcasecmp(ext, ".bin") && strcasecmp(ext, ".dat") ) == 0 )
	{
		m_sourceinfo.containertype = ctMPEGPS;
		m_sourceinfo.is_video = TRUE;
	}
	else if ( strcasecmp(ext, ".ts") == 0 )
	{
		m_sourceinfo.containertype = ctMPEGTS;
		m_sourceinfo.is_video = TRUE;
	}
	else if ( strcasecmp(ext, ".mkv") == 0 )
	{
		m_sourceinfo.containertype = ctMKV;
		m_sourceinfo.is_video = TRUE;
	}
	else if ( strcasecmp(ext, ".avi") == 0 || strcasecmp(ext, ".divx") == 0)
	{
		m_sourceinfo.containertype = ctAVI;
		m_sourceinfo.is_video = TRUE;
	}
	else if ( strcasecmp(ext, ".mp4") == 0 || strcasecmp(ext, ".mov") == 0 || strcasecmp(ext, ".m4v") == 0 || strcasecmp(ext, ".3gp") == 0 || strcasecmp(ext, ".3g2") == 0)
	{
		m_sourceinfo.containertype = ctMP4;
		m_sourceinfo.is_video = TRUE;
	}
	else if ( strcasecmp(ext, ".asf") == 0 || strcasecmp(ext, ".wmv") == 0)
	{
		m_sourceinfo.containertype = ctASF;
		m_sourceinfo.is_video = TRUE;
	}
	else if ( strcasecmp(ext, ".m4a") == 0 )
	{
		m_sourceinfo.containertype = ctMP4;
		m_sourceinfo.audiotype = atAAC;
	}
	else if ( strcasecmp(ext, ".mp3") == 0 )
		m_sourceinfo.audiotype = atMP3;
	else if ( strcasecmp(ext, ".wma") == 0 )
		m_sourceinfo.audiotype = atWMA;
	else if ( (strncmp(filename, "/autofs/", 8) || strncmp(filename+strlen(filename)-13, "/track-", 7) || strcasecmp(ext, ".wav")) == 0 )
		m_sourceinfo.containertype = ctCDA;
	if ( strcasecmp(ext, ".dat") == 0 )
	{
		m_sourceinfo.containertype = ctVCD;
		m_sourceinfo.is_video = TRUE;
	}
	if ( strstr(filename, "://") )
		m_sourceinfo.is_streaming = TRUE;

	gchar *uri;

	if ( m_sourceinfo.is_streaming )
	{
		uri = g_strdup_printf ("%s", filename);
		m_streamingsrc_timeout = eTimer::create(eApp);
		CONNECT(m_streamingsrc_timeout->timeout, eServiceMP4::sourceTimeout);

		std::string config_str;
		if( ePythonConfigQuery::getConfigValue("config.mediaplayer.useAlternateUserAgent", config_str) == 0 )
		{
			if ( config_str == "True" )
				ePythonConfigQuery::getConfigValue("config.mediaplayer.alternateUserAgent", m_useragent);
		}
		if ( m_useragent.length() == 0 )
			m_useragent = "Enigma2 Mediaplayer";

        std::string config_timeout;
        if(ePythonConfigQuery::getConfigValue("config.plugins.archivCZSK.videoPlayer.httpTimeout", config_timeout) == 0)
            m_http_timeout = atoi(config_timeout.c_str());

        std::string config_download_flag;
        if(ePythonConfigQuery::getConfigValue("config.plugins.archivCZSK.videoPlayer.download", config_download_flag) == 0)
        {
            if (config_download_flag == "True" && ::access("/hdd/movie", X_OK) >= 0 )
                {
                    /* It looks like /hdd points to a valid mount, so we can store a download buffer on it */
                    m_download_path = "/hdd/gstreamer_XXXXXXXXXX";
                    eDebug("eServiceMP4::Download mode is set");
                    m_download_mode = true;
                    m_downloadInfo.downloading = 1;
                }
        }

        std::string config_buffer_size;
        if(ePythonConfigQuery::getConfigValue("config.plugins.archivCZSK.videoPlayer.bufferSize", config_buffer_size) == 0)
            m_buffer_size = atoi(config_buffer_size.c_str())*1024;

        std::string config_buffer_duration;
        if(ePythonConfigQuery::getConfigValue("config.plugins.archivCZSK.videoPlayer.bufferDuration", config_buffer_duration) == 0)
            m_buffer_duration = atoi(config_buffer_duration.c_str());

        std::string config_buffer_mode;
        if(ePythonConfigQuery::getConfigValue("config.plugins.archivCZSK.videoPlayer.bufferMode", config_buffer_mode) == 0)
        {
            if (config_buffer_mode=="1")
            {
                m_use_prefillbuffer = true;
                eDebug("eServiceMP4::Using prefill buffering");
            }
            else if (config_buffer_mode=="2")
            {
                /* progressive download buffering */
                if (::access("/hdd/movie", X_OK) >= 0)
                {
                    /* It looks like /hdd points to a valid mount, so we can store a download buffer on it */
                    m_download_buffer_path = "/hdd/gstreamer_XXXXXXXXXX";
                    std::string config_download_buffer_size;
                    ePythonConfigQuery::getConfigValue("config.plugins.archivCZSK.videoPlayer.downloadBufferSize", config_download_buffer_size);
                    m_download_buffer_size = (guint64) ((long long)atoi(config_download_buffer_size.c_str()) * 1024LL *1024LL);
                    eDebug("eServiceMP4::Using progressive download buffering");
                }
                m_use_prefillbuffer = true;
            }
        }
	}
	else if ( m_sourceinfo.containertype == ctCDA )
	{
		int i_track = atoi(filename+18);
		uri = g_strdup_printf ("cdda://%i", i_track);
	}
	else if ( m_sourceinfo.containertype == ctVCD )
	{
		int ret = -1;
		int fd = open(filename,O_RDONLY);
		if (fd >= 0)
		{
			char tmp[128*1024];
			ret = read(fd, tmp, 128*1024);
			close(fd);
		}
		if ( ret == -1 ) // this is a "REAL" VCD
			uri = g_strdup_printf ("vcd://");
		else
			uri = g_filename_to_uri(filename, NULL, NULL);
	}
	else
		uri = g_filename_to_uri(filename, NULL, NULL);

	eDebug("eServiceMP4::playbin uri=%s", uri);
#if GST_VERSION_MAJOR < 1
	m_gst_playbin = gst_element_factory_make("playbin2", "playbin");
#else
	m_gst_playbin = gst_element_factory_make("playbin", "playbin");
#endif
	if ( m_gst_playbin )
	{
		guint flags;
		g_object_get(G_OBJECT (m_gst_playbin), "flags", &flags, NULL);
		/* avoid video conversion, let the (hardware) sinks handle that */
		flags |= GST_PLAY_FLAG_NATIVE_VIDEO;
		/* volume control is done by hardware */
		flags &= ~GST_PLAY_FLAG_SOFT_VOLUME;
		if ( m_sourceinfo.is_streaming )
		{
			g_signal_connect (G_OBJECT (m_gst_playbin), "notify::source", G_CALLBACK (playbinNotifySource), NULL);

			/* downloading */
			if (m_download_mode)
			{
			    flags |= GST_PLAY_FLAG_DOWNLOAD;
			    g_signal_connect (G_OBJECT(m_gst_playbin), "deep-notify::temp-location", G_CALLBACK (got_location), this);
				g_signal_connect(G_OBJECT(m_gst_playbin), "element-added", G_CALLBACK(handleElementAdded), this);
				m_download_poll_timer = eTimer::create(eApp);
				CONNECT(m_download_poll_timer->timeout, eServiceMP4::updateDownloadStatus);

			}

			else if (m_download_buffer_path != "")
			{
				/* use progressive download buffering */
				flags |= GST_PLAY_FLAG_DOWNLOAD;
				g_signal_connect(G_OBJECT(m_gst_playbin), "element-added", G_CALLBACK(handleElementAdded), this);
				/* limit file size */
				g_object_set(m_gst_playbin, "ring-buffer-max-size", m_download_buffer_size, NULL);
			}
			/*
			 * regardless whether or not we configured a progressive download file, use a buffer as well
			 * (progressive download might not work for all formats)
			 */
			flags |= GST_PLAY_FLAG_BUFFERING;
			/* increase the default 2 second / 2 MB buffer limitations to 5s / 5MB */

			g_object_set(G_OBJECT(m_gst_playbin), "buffer-duration", (long long) (m_buffer_duration) * GST_SECOND, NULL);
			g_object_set(G_OBJECT(m_gst_playbin), "buffer-size", m_buffer_size, NULL);
		}
		g_object_set (G_OBJECT (m_gst_playbin), "flags", flags, NULL);
		g_object_set (G_OBJECT (m_gst_playbin), "uri", uri, NULL);
		GstElement *subsink = gst_element_factory_make("subsink", "subtitle_sink");
		if (!subsink)
			eDebug("eServiceMP4::sorry, can't play: missing gst-plugin-subsink");
		else
		{
			m_subs_to_pull_handler_id = g_signal_connect (subsink, "new-buffer", G_CALLBACK (gstCBsubtitleAvail), this);
			g_object_set (G_OBJECT (subsink), "caps", gst_caps_from_string("text/plain; text/x-plain; text/x-raw; text/x-pango-markup; video/x-dvd-subpicture; subpicture/x-pgs"), NULL);
			g_object_set (G_OBJECT (m_gst_playbin), "text-sink", subsink, NULL);
			g_object_set (G_OBJECT (m_gst_playbin), "current-text", m_currentSubtitleStream, NULL);
		}
		GstBus *bus = gst_pipeline_get_bus(GST_PIPELINE (m_gst_playbin));
#if GST_VERSION_MAJOR < 1
		gst_bus_set_sync_handler(bus, gstBusSyncHandler, this);
#else
		gst_bus_set_sync_handler(bus, gstBusSyncHandler, this, NULL);
#endif
		gst_object_unref(bus);
		char srt_filename[ext - filename + 5];
		strncpy(srt_filename,filename, ext - filename);
		srt_filename[ext - filename] = '\0';
		strcat(srt_filename, ".srt");
		if (::access(srt_filename, R_OK) >= 0)
		{
			eDebug("eServiceMP4::subtitle uri: %s", g_filename_to_uri(srt_filename, NULL, NULL));
			g_object_set (G_OBJECT (m_gst_playbin), "suburi", g_filename_to_uri(srt_filename, NULL, NULL), NULL);
		}
	} else
	{
		m_event((iPlayableService*)this, evUser+12);
		m_gst_playbin = 0;
		m_errorInfo.error_message = "failed to create GStreamer pipeline!\n";

		eDebug("eServiceMP4::sorry, can't play: %s",m_errorInfo.error_message.c_str());
	}
	g_free(uri);
}

eServiceMP4::~eServiceMP4()
{
	// disconnect subtitle callback
	GstElement *subsink = gst_bin_get_by_name(GST_BIN(m_gst_playbin), "subtitle_sink");

	if (subsink)
	{
		g_signal_handler_disconnect (subsink, m_subs_to_pull_handler_id);
		gst_object_unref(subsink);
	}

	delete m_subtitle_widget;

	if (m_gst_playbin)
	{
		// disconnect sync handler callback
		GstBus *bus = gst_pipeline_get_bus(GST_PIPELINE (m_gst_playbin));
#if GST_VERSION_MAJOR < 1
		gst_bus_set_sync_handler(bus, NULL, NULL);
#else
		gst_bus_set_sync_handler(bus, NULL, NULL, NULL);
#endif
		gst_object_unref(bus);
	}

	if (m_state == stRunning)
		stop();

	if (m_stream_tags)
		gst_tag_list_free(m_stream_tags);

	if (audioSink)
	{
		gst_object_unref(GST_OBJECT(audioSink));
		audioSink = NULL;
	}
	if (videoSink)
	{
		gst_object_unref(GST_OBJECT(videoSink));
		videoSink = NULL;
	}
	if (m_gst_playbin)
	{
		gst_object_unref (GST_OBJECT (m_gst_playbin));
		eDebug("eServiceMP4::destruct!");
	}
}

DEFINE_REF(eServiceMP4);

DEFINE_REF(eServiceMP4::GstMessageContainer);

RESULT eServiceMP4::connectEvent(const Slot2<void,iPlayableService*,int> &event, ePtr<eConnection> &connection)
{
	connection = new eConnection((iPlayableService*)this, m_event.connect(event));
	return 0;
}

RESULT eServiceMP4::start()
{
	ASSERT(m_state == stIdle);

	m_state = stRunning;
	if (m_gst_playbin)
	{
		eDebug("eServiceMP4::starting pipeline");
		gst_element_set_state (m_gst_playbin, GST_STATE_PLAYING);
	}

	m_event(this, evStart);

	return 0;
}

void eServiceMP4::sourceTimeout()
{
	eDebug("eServiceMP4::http source timeout! issuing eof...");
	m_event((iPlayableService*)this, evEOF);
}

RESULT eServiceMP4::stop()
{
	ASSERT(m_state != stIdle);

	if (m_state == stStopped)
		return -1;

	eDebug("eServiceMP4::stop %s", m_ref.path.c_str());
	gst_element_set_state(m_gst_playbin, GST_STATE_NULL);
	m_state = stStopped;

	return 0;
}

RESULT eServiceMP4::setTarget(int target)
{
	return -1;
}

RESULT eServiceMP4::pause(ePtr<iPauseableService> &ptr)
{
	ptr=this;
	return 0;
}

RESULT eServiceMP4::setSlowMotion(int ratio)
{
	if (!ratio)
		return 0;
	eDebug("eServiceMP4::setSlowMotion ratio=%f",1.0/(gdouble)ratio);
	return trickSeek(1.0/(gdouble)ratio);
}

RESULT eServiceMP4::setFastForward(int ratio)
{
	eDebug("eServiceMP4::setFastForward ratio=%i",ratio);
	return trickSeek(ratio);
}

		// iPausableService
RESULT eServiceMP4::pause()
{
	if (!m_gst_playbin || m_state != stRunning)
		return -1;

    //gst_element_set_state(m_gst_playbin, GST_STATE_PAUSED);
	trickSeek(0.0);

	return 0;
}

RESULT eServiceMP4::unpause()
{
	if (!m_gst_playbin || m_state != stRunning)
		return -1;

    //gst_element_set_state(m_gst_playbin, GST_STATE_PLAYING);

	// why should we use seeking when unpause?
	trickSeek(1.0);

	return 0;
}

	/* iSeekableService */
RESULT eServiceMP4::seek(ePtr<iSeekableService> &ptr)
{
	ptr = this;
	return 0;
}

RESULT eServiceMP4::getLength(pts_t &pts)
{
	if (!m_gst_playbin)
		return -1;

	if (m_state != stRunning)
		return -1;

	GstFormat fmt = GST_FORMAT_TIME;
	gint64 len;
#if GST_VERSION_MAJOR < 1
	if (!gst_element_query_duration(m_gst_playbin, &fmt, &len))
#else
	if (!gst_element_query_duration(m_gst_playbin, fmt, &len))
#endif
		return -1;
		/* len is in nanoseconds. we have 90 000 pts per second. */

	pts = len / 11111LL;
	return 0;
}

RESULT eServiceMP4::seekToImpl(pts_t to)
{
		/* convert pts to nanoseconds */
	gint64 time_nanoseconds = to * 11111LL;
	//GST_SEEK_FLAG_KEY_UNIT
	if (!gst_element_seek (m_gst_playbin, m_currentTrickRatio, GST_FORMAT_TIME, GST_SEEK_FLAG_FLUSH,
		GST_SEEK_TYPE_SET, time_nanoseconds,
		GST_SEEK_TYPE_NONE, GST_CLOCK_TIME_NONE))
	{
		eDebug("eServiceMP4::seekTo failed");
		return -1;
	}

	return 0;
}

RESULT eServiceMP4::seekTo(pts_t to)
{
	RESULT ret = -1;

	if (m_gst_playbin)
	{
		m_subtitle_pages.clear();
		m_prev_decoder_time = -1;
		m_decoder_time_valid_state = 0;
		ret = seekToImpl(to);
	}

	return ret;
}


RESULT eServiceMP4::trickSeek(gdouble ratio)
{
	if (!m_gst_playbin)
		return -1;
	if (ratio > -0.01 && ratio < 0.01)
	{
		gst_element_set_state(m_gst_playbin, GST_STATE_PAUSED);
		return 0;
	}

	m_currentTrickRatio = ratio;

	bool validposition = false;
	gint64 pos = 0;
	pts_t pts;
	if (getPlayPosition(pts) >= 0)
	{
		validposition = true;
		pos = pts * 11111LL;
	}

	gst_element_set_state(m_gst_playbin, GST_STATE_PLAYING);

	if (validposition)
	{
		if (ratio >= 0.0)
		{
			gst_element_seek(m_gst_playbin, ratio, GST_FORMAT_TIME, (GstSeekFlags)(GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_SKIP), GST_SEEK_TYPE_SET, pos, GST_SEEK_TYPE_SET, -1);
		}
		else
		{
			/* note that most elements will not support negative speed */
			gst_element_seek(m_gst_playbin, ratio, GST_FORMAT_TIME, (GstSeekFlags)(GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_SKIP), GST_SEEK_TYPE_SET, 0, GST_SEEK_TYPE_SET, pos);
		}
	}

	m_subtitle_pages.clear();
	m_prev_decoder_time = -1;
	m_decoder_time_valid_state = 0;
	return 0;
}


RESULT eServiceMP4::seekRelative(int direction, pts_t to)
{
	if (!m_gst_playbin)
		return -1;

	pts_t ppos;
	if (getPlayPosition(ppos) < 0) return -1;
	ppos += to * direction;
	if (ppos < 0)
		ppos = 0;
	return seekTo(ppos);
}

gint eServiceMP4::match_sinktype(GstElement *element, gpointer type)
{
	return strcmp(g_type_name(G_OBJECT_TYPE(element)), (const char*)type);
}

RESULT eServiceMP4::getPlayPosition(pts_t &pts)
{
	gint64 pos;
	pts = 0;

	if (!m_gst_playbin)
		return -1;
	if (m_state != stRunning)
		return -1;

	if (audioSink || videoSink)
	{
		g_signal_emit_by_name(audioSink ? audioSink : videoSink, "get-decoder-time", &pos);
		if (!GST_CLOCK_TIME_IS_VALID(pos)) return -1;
	}
	else
	{
		GstFormat fmt = GST_FORMAT_TIME;
#if GST_VERSION_MAJOR < 1
		if (!gst_element_query_position(m_gst_playbin, &fmt, &pos))
#else
		if (!gst_element_query_position(m_gst_playbin, fmt, &pos))
#endif
		{
			eDebug("gst_element_query_position failed in getPlayPosition");
			return -1;
		}
	}

	/* pos is in nanoseconds. we have 90 000 pts per second. */
	pts = pos / 11111LL;
	return 0;
}

RESULT eServiceMP4::setTrickmode(int trick)
{
		/* trickmode is not yet supported by our dvbmediasinks. */
	return -1;
}

RESULT eServiceMP4::isCurrentlySeekable()
{
	int ret = 3; /* just assume that seeking and fast/slow winding are possible */

	if (!m_gst_playbin)
		return 0;
	if (m_state != stRunning)
		return 0;

	return ret;
}

RESULT eServiceMP4::info(ePtr<iServiceInformation>&i)
{
	i = this;
	return 0;
}

RESULT eServiceMP4::getName(std::string &name)
{
	std::string title = m_ref.getName();
	if (title.empty())
	{
		name = m_ref.path;
		size_t n = name.rfind('/');
		if (n != std::string::npos)
			name = name.substr(n + 1);
	}
	else
		name = title;
	return 0;
}

int eServiceMP4::getInfo(int w)
{
	const gchar *tag = 0;

	switch (w)
	{
	case sServiceref: return m_ref;
	case sVideoHeight: return m_height;
	case sVideoWidth: return m_width;
	case sFrameRate: return m_framerate;
	case sProgressive: return m_progressive;
	case sAspect: return m_aspect;
	case sTagTitle:
	case sTagArtist:
	case sTagAlbum:
	case sTagTitleSortname:
	case sTagArtistSortname:
	case sTagAlbumSortname:
	case sTagDate:
	case sTagComposer:
	case sTagGenre:
	case sTagComment:
	case sTagExtendedComment:
	case sTagLocation:
	case sTagHomepage:
	case sTagDescription:
	case sTagVersion:
	case sTagISRC:
	case sTagOrganization:
	case sTagCopyright:
	case sTagCopyrightURI:
	case sTagContact:
	case sTagLicense:
	case sTagLicenseURI:
	case sTagCodec:
	case sTagAudioCodec:
	case sTagVideoCodec:
	case sTagEncoder:
	case sTagLanguageCode:
	case sTagKeywords:
	case sTagChannelMode:
	case sUser+12:
		return resIsString;
	case sTagTrackGain:
	case sTagTrackPeak:
	case sTagAlbumGain:
	case sTagAlbumPeak:
	case sTagReferenceLevel:
	case sTagBeatsPerMinute:
	case sTagImage:
	case sTagPreviewImage:
	case sTagAttachment:
		return resIsPyObject;
	case sTagTrackNumber:
		tag = GST_TAG_TRACK_NUMBER;
		break;
	case sTagTrackCount:
		tag = GST_TAG_TRACK_COUNT;
		break;
	case sTagAlbumVolumeNumber:
		tag = GST_TAG_ALBUM_VOLUME_NUMBER;
		break;
	case sTagAlbumVolumeCount:
		tag = GST_TAG_ALBUM_VOLUME_COUNT;
		break;
	case sTagBitrate:
		tag = GST_TAG_BITRATE;
		break;
	case sTagNominalBitrate:
		tag = GST_TAG_NOMINAL_BITRATE;
		break;
	case sTagMinimumBitrate:
		tag = GST_TAG_MINIMUM_BITRATE;
		break;
	case sTagMaximumBitrate:
		tag = GST_TAG_MAXIMUM_BITRATE;
		break;
	case sTagSerial:
		tag = GST_TAG_SERIAL;
		break;
	case sTagEncoderVersion:
		tag = GST_TAG_ENCODER_VERSION;
		break;
	case sTagCRC:
		tag = "has-crc";
		break;
	default:
		return resNA;
	}

	if (!m_stream_tags || !tag)
		return 0;

	guint value;
	if (gst_tag_list_get_uint(m_stream_tags, tag, &value))
		return (int) value;

	return 0;
}

std::string eServiceMP4::getInfoString(int w)
{
	if ( !m_stream_tags && w < sUser && w > 26 )
		return "";
	const gchar *tag = 0;
	switch (w)
	{
	case sTagTitle:
		tag = GST_TAG_TITLE;
		break;
	case sTagArtist:
		tag = GST_TAG_ARTIST;
		break;
	case sTagAlbum:
		tag = GST_TAG_ALBUM;
		break;
	case sTagTitleSortname:
		tag = GST_TAG_TITLE_SORTNAME;
		break;
	case sTagArtistSortname:
		tag = GST_TAG_ARTIST_SORTNAME;
		break;
	case sTagAlbumSortname:
		tag = GST_TAG_ALBUM_SORTNAME;
		break;
	case sTagDate:
		GDate *date;
		if (gst_tag_list_get_date(m_stream_tags, GST_TAG_DATE, &date))
		{
			gchar res[5];
 			g_date_strftime (res, sizeof(res), "%Y-%M-%D", date);
			return (std::string)res;
		}
		break;
	case sTagComposer:
		tag = GST_TAG_COMPOSER;
		break;
	case sTagGenre:
		tag = GST_TAG_GENRE;
		break;
	case sTagComment:
		tag = GST_TAG_COMMENT;
		break;
	case sTagExtendedComment:
		tag = GST_TAG_EXTENDED_COMMENT;
		break;
	case sTagLocation:
		tag = GST_TAG_LOCATION;
		break;
	case sTagHomepage:
		tag = GST_TAG_HOMEPAGE;
		break;
	case sTagDescription:
		tag = GST_TAG_DESCRIPTION;
		break;
	case sTagVersion:
		tag = GST_TAG_VERSION;
		break;
	case sTagISRC:
		tag = GST_TAG_ISRC;
		break;
	case sTagOrganization:
		tag = GST_TAG_ORGANIZATION;
		break;
	case sTagCopyright:
		tag = GST_TAG_COPYRIGHT;
		break;
	case sTagCopyrightURI:
		tag = GST_TAG_COPYRIGHT_URI;
		break;
	case sTagContact:
		tag = GST_TAG_CONTACT;
		break;
	case sTagLicense:
		tag = GST_TAG_LICENSE;
		break;
	case sTagLicenseURI:
		tag = GST_TAG_LICENSE_URI;
		break;
	case sTagCodec:
		tag = GST_TAG_CODEC;
		break;
	case sTagAudioCodec:
		tag = GST_TAG_AUDIO_CODEC;
		break;
	case sTagVideoCodec:
		tag = GST_TAG_VIDEO_CODEC;
		break;
	case sTagEncoder:
		tag = GST_TAG_ENCODER;
		break;
	case sTagLanguageCode:
		tag = GST_TAG_LANGUAGE_CODE;
		break;
	case sTagKeywords:
		tag = GST_TAG_KEYWORDS;
		break;
	case sTagChannelMode:
		tag = "channel-mode";
		break;
	case sUser+12:
		return m_errorInfo.error_message;
	default:
		return "";
	}
	if ( !tag )
		return "";
	gchar *value;
	if (m_stream_tags && gst_tag_list_get_string(m_stream_tags, tag, &value))
	{
		std::string res = value;
		g_free(value);
		return res;
	}
	return "";
}

PyObject *eServiceMP4::getInfoObject(int w)
{
	const gchar *tag = 0;
	bool isBuffer = false;
	switch (w)
	{
		case sTagTrackGain:
			tag = GST_TAG_TRACK_GAIN;
			break;
		case sTagTrackPeak:
			tag = GST_TAG_TRACK_PEAK;
			break;
		case sTagAlbumGain:
			tag = GST_TAG_ALBUM_GAIN;
			break;
		case sTagAlbumPeak:
			tag = GST_TAG_ALBUM_PEAK;
			break;
		case sTagReferenceLevel:
			tag = GST_TAG_REFERENCE_LEVEL;
			break;
		case sTagBeatsPerMinute:
			tag = GST_TAG_BEATS_PER_MINUTE;
			break;
		case sTagImage:
			tag = GST_TAG_IMAGE;
			isBuffer = true;
			break;
		case sTagPreviewImage:
			tag = GST_TAG_PREVIEW_IMAGE;
			isBuffer = true;
			break;
		case sTagAttachment:
			tag = GST_TAG_ATTACHMENT;
			isBuffer = true;
			break;
		default:
			break;
	}

	if (m_stream_tags && tag)
	{
		if (isBuffer)
		{
			const GValue *gv_buffer = gst_tag_list_get_value_index(m_stream_tags, tag, 0);
			if ( gv_buffer )
			{
				PyObject *retval = NULL;
				guint8 *data;
				gsize size;
				GstBuffer *buffer;
				buffer = gst_value_get_buffer (gv_buffer);
#if GST_VERSION_MAJOR < 1
				data = GST_BUFFER_DATA(buffer);
				size = GST_BUFFER_SIZE(buffer);
#else
				GstMapInfo map;
				gst_buffer_map(buffer, &map, GST_MAP_READ);
				data = map.data;
				size = map.size;
#endif
				retval = PyBuffer_FromMemory(data, size);
#if GST_VERSION_MAJOR >= 1
				gst_buffer_unmap(buffer, &map);
#endif
				return retval;
			}
		}
		else
		{
			gdouble value = 0.0;
			gst_tag_list_get_double(m_stream_tags, tag, &value);
			return PyFloat_FromDouble(value);
		}
	}

	Py_RETURN_NONE;
}

RESULT eServiceMP4::audioChannel(ePtr<iAudioChannelSelection> &ptr)
{
	ptr = this;
	return 0;
}

RESULT eServiceMP4::audioTracks(ePtr<iAudioTrackSelection> &ptr)
{
	ptr = this;
	return 0;
}

RESULT eServiceMP4::subtitle(ePtr<iSubtitleOutput> &ptr)
{
	ptr = this;
	return 0;
}

RESULT eServiceMP4::audioDelay(ePtr<iAudioDelay> &ptr)
{
	ptr = this;
	return 0;
}

int eServiceMP4::getNumberOfTracks()
{
 	return m_audioStreams.size();
}

int eServiceMP4::getCurrentTrack()
{
	if (m_currentAudioStream == -1)
		g_object_get (G_OBJECT (m_gst_playbin), "current-audio", &m_currentAudioStream, NULL);
	return m_currentAudioStream;
}

RESULT eServiceMP4::selectTrack(unsigned int i)
{
	bool validposition = false;
	pts_t ppos = 0;
	if (getPlayPosition(ppos) >= 0)
	{
		validposition = true;
		ppos -= 90000;
		if (ppos < 0)
			ppos = 0;
	}

	int ret = selectAudioStream(i);
	if (!ret)
	{
		if (validposition)
		{
			/* flush */
			seekTo(ppos);
		}
	}

	return ret;
}

int eServiceMP4::selectAudioStream(int i)
{
	int current_audio;
	g_object_set (G_OBJECT (m_gst_playbin), "current-audio", i, NULL);
	g_object_get (G_OBJECT (m_gst_playbin), "current-audio", &current_audio, NULL);
	if ( current_audio == i )
	{
		eDebug ("eServiceMP4::switched to audio stream %i", current_audio);
		m_currentAudioStream = i;
		return 0;
	}
	return -1;
}

int eServiceMP4::getCurrentChannel()
{
	return STEREO;
}

RESULT eServiceMP4::selectChannel(int i)
{
	eDebug("eServiceMP4::selectChannel(%i)",i);
	return 0;
}

RESULT eServiceMP4::getTrackInfo(struct iAudioTrackInfo &info, unsigned int i)
{
 	if (i >= m_audioStreams.size())
		return -2;
		info.m_description = m_audioStreams[i].codec;
/*	if (m_audioStreams[i].type == atMPEG)
		info.m_description = "MPEG";
	else if (m_audioStreams[i].type == atMP3)
		info.m_description = "MP3";
	else if (m_audioStreams[i].type == atAC3)
		info.m_description = "AC3";
	else if (m_audioStreams[i].type == atAAC)
		info.m_description = "AAC";
	else if (m_audioStreams[i].type == atDTS)
		info.m_description = "DTS";
	else if (m_audioStreams[i].type == atPCM)
		info.m_description = "PCM";
	else if (m_audioStreams[i].type == atOGG)
		info.m_description = "OGG";
	else if (m_audioStreams[i].type == atFLAC)
		info.m_description = "FLAC";
	else
		info.m_description = "???";*/
	if (info.m_language.empty())
		info.m_language = m_audioStreams[i].language_code;
	return 0;
}

subtype_t getSubtitleType(GstPad* pad, gchar *g_codec=NULL)
{
	subtype_t type = stUnknown;
#if GST_VERSION_MAJOR < 1
	GstCaps* caps = gst_pad_get_negotiated_caps(pad);
#else
	GstCaps* caps = gst_pad_get_current_caps(pad);
#endif
	if (!caps && !g_codec)
	{
		caps = gst_pad_get_allowed_caps(pad);
	}

	if (caps && !gst_caps_is_empty(caps))
	{
		GstStructure* str = gst_caps_get_structure(caps, 0);
		if (str)
		{
			const gchar *g_type = gst_structure_get_name(str);
			eDebug("getSubtitleType::subtitle probe caps type=%s", g_type ? g_type : "(null)");
			if (g_type)
			{
				if ( !strcmp(g_type, "video/x-dvd-subpicture") )
					type = stVOB;
				else if ( !strcmp(g_type, "text/x-pango-markup") )
					type = stSRT;
				else if ( !strcmp(g_type, "text/plain") || !strcmp(g_type, "text/x-plain") || !strcmp(g_type, "text/x-raw") )
					type = stPlainText;
				else if ( !strcmp(g_type, "subpicture/x-pgs") )
					type = stPGS;
				else
					eDebug("getSubtitleType::unsupported subtitle caps %s (%s)", g_type, g_codec ? g_codec : "(null)");
			}
		}
	}
	else if ( g_codec )
	{
		eDebug("getSubtitleType::subtitle probe codec tag=%s", g_codec);
		if ( !strcmp(g_codec, "VOB") )
			type = stVOB;
		else if ( !strcmp(g_codec, "SubStation Alpha") || !strcmp(g_codec, "SSA") )
			type = stSSA;
		else if ( !strcmp(g_codec, "ASS") )
			type = stASS;
		else if ( !strcmp(g_codec, "SRT") )
			type = stSRT;
		else if ( !strcmp(g_codec, "UTF-8 plain text") )
			type = stPlainText;
		else
			eDebug("getSubtitleType::unsupported subtitle codec %s", g_codec);
	}
	else
		eDebug("getSubtitleType::unidentifiable subtitle stream!");

	return type;
}

void eServiceMP4::gstBusCall(GstMessage *msg)
{
	if (!msg)
		return;
	gchar *sourceName;
	GstObject *source;
	source = GST_MESSAGE_SRC(msg);
	if (!GST_IS_OBJECT(source))
		return;
	sourceName = gst_object_get_name(source);
#if 0
	gchar *string;
	if (gst_message_get_structure(msg))
		string = gst_structure_to_string(gst_message_get_structure(msg));
	else
		string = g_strdup(GST_MESSAGE_TYPE_NAME(msg));
	eDebug("eTsRemoteSource::gst_message from %s: %s", sourceName, string);
	g_free(string);
#endif
	switch (GST_MESSAGE_TYPE (msg))
	{
		case GST_MESSAGE_EOS:
			m_event((iPlayableService*)this, evEOF);
			break;
		case GST_MESSAGE_STATE_CHANGED:
		{
			if(GST_MESSAGE_SRC(msg) != GST_OBJECT(m_gst_playbin))
				break;

			GstState old_state, new_state;
			gst_message_parse_state_changed(msg, &old_state, &new_state, NULL);

			if(old_state == new_state)
				break;

			eDebug("eServiceMP4::state transition %s -> %s", gst_element_state_get_name(old_state), gst_element_state_get_name(new_state));

			GstStateChange transition = (GstStateChange)GST_STATE_TRANSITION(old_state, new_state);

			switch(transition)
			{
				case GST_STATE_CHANGE_NULL_TO_READY:
				{
				}	break;
				case GST_STATE_CHANGE_READY_TO_PAUSED:
				{
#if GST_VERSION_MAJOR >= 1
					GValue element = { 0, };
#endif
					GstIterator *children;
					GstElement *subsink = gst_bin_get_by_name(GST_BIN(m_gst_playbin), "subtitle_sink");
					if (subsink)
					{
#ifdef GSTREAMER_SUBTITLE_SYNC_MODE_BUG
						/*
						 * HACK: disable sync mode for now, gstreamer suffers from a bug causing sparse streams to loose sync, after pause/resume / skip
						 * see: https://bugzilla.gnome.org/show_bug.cgi?id=619434
						 * Sideeffect of using sync=false is that we receive subtitle buffers (far) ahead of their
						 * display time.
						 * Not too far ahead for subtitles contained in the media container.
						 * But for external srt files, we could receive all subtitles at once.
						 * And not just once, but after each pause/resume / skip.
						 * So as soon as gstreamer has been fixed to keep sync in sparse streams, sync needs to be re-enabled.
						 */
						g_object_set (G_OBJECT (subsink), "sync", FALSE, NULL);
#endif
#if 0
						/* we should not use ts-offset to sync with the decoder time, we have to do our own decoder timekeeping */
						g_object_set (G_OBJECT (subsink), "ts-offset", -2LL * GST_SECOND, NULL);
						/* late buffers probably will not occur very often */
						g_object_set (G_OBJECT (subsink), "max-lateness", 0LL, NULL);
						/* avoid prerolling (it might not be a good idea to preroll a sparse stream) */
						g_object_set (G_OBJECT (subsink), "async", TRUE, NULL);
#endif
						eDebug("eServiceMP4::subsink properties set!");
						gst_object_unref(subsink);
					}
					if (audioSink)
					{
						gst_object_unref(GST_OBJECT(audioSink));
						audioSink = NULL;
					}
					if (videoSink)
					{
						gst_object_unref(GST_OBJECT(videoSink));
						videoSink = NULL;
					}
					children = gst_bin_iterate_recurse(GST_BIN(m_gst_playbin));
#if GST_VERSION_MAJOR < 1
					audioSink = GST_ELEMENT_CAST(gst_iterator_find_custom(children, (GCompareFunc)match_sinktype, (gpointer)"GstDVBAudioSink"));
#else
					if (gst_iterator_find_custom(children, (GCompareFunc)match_sinktype, &element, (gpointer)"GstDVBAudioSink"))
					{
						audioSink = g_value_dup_object(&element);
						g_value_unset(&element);
					}
#endif
					gst_iterator_free(children);
					children = gst_bin_iterate_recurse(GST_BIN(m_gst_playbin));
#if GST_VERSION_MAJOR < 1
					videoSink = GST_ELEMENT_CAST(gst_iterator_find_custom(children, (GCompareFunc)match_sinktype, (gpointer)"GstDVBVideoSink"));
#else
					if (gst_iterator_find_custom(children, (GCompareFunc)match_sinktype, &element, (gpointer)"GstDVBVideoSink"))
					{
						videoSink = g_value_dup_object(&element);
						g_value_unset(&element);
					}
#endif
					gst_iterator_free(children);

					m_is_live = (gst_element_get_state(m_gst_playbin, NULL, NULL, 0LL) == GST_STATE_CHANGE_NO_PREROLL);

					setAC3Delay(ac3_delay);
					setPCMDelay(pcm_delay);
				}	break;
				case GST_STATE_CHANGE_PAUSED_TO_PLAYING:
				{
					if ( m_sourceinfo.is_streaming && m_streamingsrc_timeout )
						m_streamingsrc_timeout->stop();
				}	break;
				case GST_STATE_CHANGE_PLAYING_TO_PAUSED:
				{
				}	break;
				case GST_STATE_CHANGE_PAUSED_TO_READY:
				{
					if (audioSink)
					{
						gst_object_unref(GST_OBJECT(audioSink));
						audioSink = NULL;
					}
					if (videoSink)
					{
						gst_object_unref(GST_OBJECT(videoSink));
						videoSink = NULL;
					}
				}	break;
				case GST_STATE_CHANGE_READY_TO_NULL:
				{
				}	break;
			}
			break;
		}
		case GST_MESSAGE_ERROR:
		{
			gchar *debug;
			GError *err;
			gst_message_parse_error (msg, &err, &debug);
			g_free (debug);
			eWarning("Gstreamer error: %s (%i) from %s", err->message, err->code, sourceName );
			if ( err->domain == GST_STREAM_ERROR )
			{
				if ( err->code == GST_STREAM_ERROR_CODEC_NOT_FOUND )
				{
					if ( g_strrstr(sourceName, "videosink") )
						m_event((iPlayableService*)this, evUser+11);
					else if ( g_strrstr(sourceName, "audiosink") )
						m_event((iPlayableService*)this, evUser+10);
				}
			}
			g_error_free(err);
			break;
		}
		case GST_MESSAGE_INFO:
		{
			gchar *debug;
			GError *inf;

			gst_message_parse_info (msg, &inf, &debug);
			g_free (debug);
			if ( inf->domain == GST_STREAM_ERROR && inf->code == GST_STREAM_ERROR_DECODE )
			{
				if ( g_strrstr(sourceName, "videosink") )
					m_event((iPlayableService*)this, evUser+14);
			}
			g_error_free(inf);
			break;
		}
		case GST_MESSAGE_TAG:
		{
			GstTagList *tags, *result;
			gst_message_parse_tag(msg, &tags);

			result = gst_tag_list_merge(m_stream_tags, tags, GST_TAG_MERGE_REPLACE);
			if (result)
			{
				if (m_stream_tags)
					gst_tag_list_free(m_stream_tags);
				m_stream_tags = result;
			}

			const GValue *gv_image = gst_tag_list_get_value_index(tags, GST_TAG_IMAGE, 0);
			if ( gv_image )
			{
				GstBuffer *buf_image;
				buf_image = gst_value_get_buffer (gv_image);
				int fd = open("/tmp/.id3coverart", O_CREAT|O_WRONLY|O_TRUNC, 0644);
				if (fd >= 0)
				{
					guint8 *data;
					gsize size;
#if GST_VERSION_MAJOR < 1
					data = GST_BUFFER_DATA(buf_image);
					size = GST_BUFFER_SIZE(buf_image);
#else
					GstMapInfo map;
					gst_buffer_map(buf_image, &map, GST_MAP_READ);
					data = map.data;
					size = map.size;
#endif
					int ret = write(fd, data, size);
#if GST_VERSION_MAJOR >= 1
					gst_buffer_unmap(buf_image, &map);
#endif
					close(fd);
					eDebug("eServiceMP4::/tmp/.id3coverart %d bytes written ", ret);
				}
				m_event((iPlayableService*)this, evUser+13);
			}
			gst_tag_list_free(tags);
			m_event((iPlayableService*)this, evUpdatedInfo);
			break;
		}
		case GST_MESSAGE_ASYNC_DONE:
		{
			if(GST_MESSAGE_SRC(msg) != GST_OBJECT(m_gst_playbin))
				break;

			gint i, n_video = 0, n_audio = 0, n_text = 0;

			g_object_get (m_gst_playbin, "n-video", &n_video, NULL);
			g_object_get (m_gst_playbin, "n-audio", &n_audio, NULL);
			g_object_get (m_gst_playbin, "n-text", &n_text, NULL);

			eDebug("eServiceMP4::async-done - %d video, %d audio, %d subtitle", n_video, n_audio, n_text);

			if ( n_video + n_audio <= 0 )
				stop();

			m_audioStreams.clear();
			m_subtitleStreams.clear();

			for (i = 0; i < n_audio; i++)
			{
				audioStream audio;
				gchar *g_codec, *g_lang;
				GstTagList *tags = NULL;
				GstPad* pad = 0;
				g_signal_emit_by_name (m_gst_playbin, "get-audio-pad", i, &pad);
#if GST_VERSION_MAJOR < 1
				GstCaps* caps = gst_pad_get_negotiated_caps(pad);
#else
				GstCaps* caps = gst_pad_get_current_caps(pad);
#endif
				if (!caps)
					continue;
				GstStructure* str = gst_caps_get_structure(caps, 0);
				const gchar *g_type = gst_structure_get_name(str);
				eDebug("AUDIO STRUCT=%s", g_type);
				audio.type = gstCheckAudioPad(str);
				audio.language_code = "und";
				audio.codec = g_type;
				g_codec = NULL;
				g_lang = NULL;
				g_signal_emit_by_name (m_gst_playbin, "get-audio-tags", i, &tags);
#if GST_VERSION_MAJOR < 1
				if (tags && gst_is_tag_list(tags))
#else
				if (tags && GST_IS_TAG_LIST(tags))
#endif
				{
					if (gst_tag_list_get_string(tags, GST_TAG_AUDIO_CODEC, &g_codec))
					{
						audio.codec = std::string(g_codec);
						g_free(g_codec);
					}
					if (gst_tag_list_get_string(tags, GST_TAG_LANGUAGE_CODE, &g_lang))
					{
						audio.language_code = std::string(g_lang);
						g_free(g_lang);
					}
					gst_tag_list_free(tags);
				}
				eDebug("eServiceMP4::audio stream=%i codec=%s language=%s", i, audio.codec.c_str(), audio.language_code.c_str());
				m_audioStreams.push_back(audio);
				gst_caps_unref(caps);
			}

			for (i = 0; i < n_text; i++)
			{
				gchar *g_codec = NULL, *g_lang = NULL;
				GstTagList *tags = NULL;
				g_signal_emit_by_name (m_gst_playbin, "get-text-tags", i, &tags);
				subtitleStream subs;
				subs.language_code = "und";
#if GST_VERSION_MAJOR < 1
				if (tags && gst_is_tag_list(tags))
#else
				if (tags && GST_IS_TAG_LIST(tags))
#endif
				{
					if (gst_tag_list_get_string(tags, GST_TAG_LANGUAGE_CODE, &g_lang))
					{
						subs.language_code = g_lang;
						g_free(g_lang);
					}
					gst_tag_list_get_string(tags, GST_TAG_SUBTITLE_CODEC, &g_codec);
					gst_tag_list_free(tags);
				}

				eDebug("eServiceMP4::subtitle stream=%i language=%s codec=%s", i, subs.language_code.c_str(), g_codec ? g_codec : "(null)");

				GstPad* pad = 0;
				g_signal_emit_by_name (m_gst_playbin, "get-text-pad", i, &pad);
				if ( pad )
					g_signal_connect (G_OBJECT (pad), "notify::caps", G_CALLBACK (gstTextpadHasCAPS), this);

				subs.type = getSubtitleType(pad, g_codec);
				g_free(g_codec);
				m_subtitleStreams.push_back(subs);
			}
			m_event((iPlayableService*)this, evUpdatedInfo);

			if ( m_errorInfo.missing_codec != "" )
			{
				if (m_errorInfo.missing_codec.find("video/") == 0 || (m_errorInfo.missing_codec.find("audio/") == 0 && m_audioStreams.empty()))
					m_event((iPlayableService*)this, evUser+12);
			}
			break;
		}
		case GST_MESSAGE_ELEMENT:
		{
			const GstStructure *msgstruct = gst_message_get_structure(msg);
			if (msgstruct)
			{
				if ( gst_is_missing_plugin_message(msg) )
				{
					GstCaps *caps = NULL;
					gst_structure_get (msgstruct, "detail", GST_TYPE_CAPS, &caps, NULL);
					if (caps)
					{
						std::string codec = (const char*) gst_caps_to_string(caps);
						gchar *description = gst_missing_plugin_message_get_description(msg);
						if ( description )
						{
							eDebug("eServiceMP4::m_errorInfo.missing_codec = %s", codec.c_str());
							m_errorInfo.error_message = "GStreamer plugin " + (std::string)description + " not available!\n";
							m_errorInfo.missing_codec = codec.substr(0,(codec.find_first_of(',')));
							g_free(description);
						}
						gst_caps_unref(caps);
					}
				}
				else
				{
					const gchar *eventname = gst_structure_get_name(msgstruct);
					if ( eventname )
					{
						if (!strcmp(eventname, "eventSizeChanged") || !strcmp(eventname, "eventSizeAvail"))
						{
							gst_structure_get_int (msgstruct, "aspect_ratio", &m_aspect);
							gst_structure_get_int (msgstruct, "width", &m_width);
							gst_structure_get_int (msgstruct, "height", &m_height);
							if (strstr(eventname, "Changed"))
								m_event((iPlayableService*)this, evVideoSizeChanged);
						}
						else if (!strcmp(eventname, "eventFrameRateChanged") || !strcmp(eventname, "eventFrameRateAvail"))
						{
							gst_structure_get_int (msgstruct, "frame_rate", &m_framerate);
							if (strstr(eventname, "Changed"))
								m_event((iPlayableService*)this, evVideoFramerateChanged);
						}
						else if (!strcmp(eventname, "eventProgressiveChanged") || !strcmp(eventname, "eventProgressiveAvail"))
						{
							gst_structure_get_int (msgstruct, "progressive", &m_progressive);
							if (strstr(eventname, "Changed"))
								m_event((iPlayableService*)this, evVideoProgressiveChanged);
						}
						else if (!strcmp(eventname, "redirect"))
						{
							const char *uri = gst_structure_get_string(msgstruct, "new-location");
							eDebug("redirect to %s", uri);
							gst_element_set_state (m_gst_playbin, GST_STATE_NULL);
							g_object_set(G_OBJECT (m_gst_playbin), "uri", uri, NULL);
							gst_element_set_state (m_gst_playbin, GST_STATE_PLAYING);
						}
					}
				}
			}
			break;
		}
		case GST_MESSAGE_BUFFERING:
			if (m_state == stRunning && m_sourceinfo.is_streaming)
			{
				GstBufferingMode mode;
				gst_message_parse_buffering(msg, &(m_bufferInfo.bufferPercent));
				eDebug("Buffering %u percent done", m_bufferInfo.bufferPercent);
				gst_message_parse_buffering_stats(msg, &mode, &(m_bufferInfo.avgInRate), &(m_bufferInfo.avgOutRate), &(m_bufferInfo.bufferingLeft));
				m_event((iPlayableService*)this, evBuffering);
				/*
				 * we don't react to buffer level messages, unless we are configured to use a prefill buffer
				 * (even if we are not configured to, we still use the buffer, but we rely on it to remain at the
				 * healthy level at all times, without ever having to pause the stream)
				 *
				 * Also, it does not make sense to pause the stream if it is a live stream
				 * (in which case the sink will not produce data while paused, so we won't
				 * recover from an empty buffer)
				 */
				if (m_use_prefillbuffer && !m_is_live && --m_ignore_buffering_messages <= 0)
				{
					if (m_bufferInfo.bufferPercent == 100)
					{
						GstState state;
						gst_element_get_state(m_gst_playbin, &state, NULL, 0LL);
						if (state != GST_STATE_PLAYING)
						{
							eDebug("start playing");
							gst_element_set_state (m_gst_playbin, GST_STATE_PLAYING);
						}
						/*
						 * when we start the pipeline, the contents of the buffer will immediately drain
						 * into the (hardware buffers of the) sinks, so we will receive low buffer level
						 * messages right away.
						 * Ignore the first few buffering messages, giving the buffer the chance to recover
						 * a bit, before we start handling empty buffer states again.
						 */
						m_ignore_buffering_messages = 5;
					}
					else if (m_bufferInfo.bufferPercent == 0)
					{
						eDebug("start pause");
						gst_element_set_state (m_gst_playbin, GST_STATE_PAUSED);
						m_ignore_buffering_messages = 0;
					}
					else
					{
						m_ignore_buffering_messages = 0;
					}
				}
			}
			break;
		case GST_MESSAGE_STREAM_STATUS:
		{
			GstStreamStatusType type;
			GstElement *owner;
			gst_message_parse_stream_status (msg, &type, &owner);
			if ( type == GST_STREAM_STATUS_TYPE_CREATE && m_sourceinfo.is_streaming )
			{
				if ( GST_IS_PAD(source) )
					owner = gst_pad_get_parent_element(GST_PAD(source));
				else if ( GST_IS_ELEMENT(source) )
					owner = GST_ELEMENT(source);
				else
					owner = 0;
				if ( owner )
				{
					GstElementFactory *factory = gst_element_get_factory(GST_ELEMENT(owner));
					const gchar *name = gst_plugin_feature_get_name(GST_PLUGIN_FEATURE(factory));
					if (!strcmp(name, "souphttpsrc"))
					{
						m_streamingsrc_timeout->start(m_http_timeout*1000, true);
						g_object_set (G_OBJECT (owner), "timeout", m_http_timeout, NULL);
						eDebug("eServiceMP4::GST_STREAM_STATUS_TYPE_CREATE -> setting timeout on %s to %is", name, m_http_timeout);
					}
				}
				if ( GST_IS_PAD(source) )
					gst_object_unref(owner);
			}
			break;
        case GST_MESSAGE_CLOCK_LOST:
            /* Get a new clock */
            gst_element_set_state (m_gst_playbin, GST_STATE_PAUSED);
            gst_element_set_state (m_gst_playbin, GST_STATE_PLAYING);
        break;
		}
		default:
			break;
	}
	g_free (sourceName);
}

void eServiceMP4::handleMessage(GstMessage *msg)
{
	if (GST_MESSAGE_TYPE(msg) == GST_MESSAGE_STATE_CHANGED && GST_MESSAGE_SRC(msg) != GST_OBJECT(m_gst_playbin))
	{
		/*
		 * ignore verbose state change messages for all active elements;
		 * we only need to handle state-change events for the playbin
		 */
		gst_message_unref(msg);
		return;
	}
	m_pump.send(new GstMessageContainer(1, msg, NULL, NULL));
}

GstBusSyncReply eServiceMP4::gstBusSyncHandler(GstBus *bus, GstMessage *message, gpointer user_data)
{
	eServiceMP4 *_this = (eServiceMP4*)user_data;
	if (_this) _this->handleMessage(message);
	return GST_BUS_DROP;
}

void eServiceMP4::playbinNotifySource(GObject *object, GParamSpec *unused, gpointer data)
{
	char header[400];
	char head[100];
	char value[100];

    const char *p;
    int len = 0;
    int len2 = 0;
    int len1 = 0;

	GValue headerValue;
	GstElement *source = NULL;
	g_object_get(object, "source", &source, NULL);
	if (source)
	{
        std::string user_agent;
        ePythonConfigQuery::getConfigValue("config.plugins.archivCZSK.videoPlayer.userAgent", user_agent);

        if (g_object_class_find_property(G_OBJECT_GET_CLASS(source), "user-agent") != 0 && user_agent != "")
        {
            g_object_set(G_OBJECT(source), "user-agent", user_agent.c_str(), NULL);
        }

        std::string extra_headers;
        ePythonConfigQuery::getConfigValue("config.plugins.archivCZSK.videoPlayer.extraHeaders", extra_headers);

        if (g_object_class_find_property(G_OBJECT_GET_CLASS(source), "extra-headers") != 0 && extra_headers != "")
        {
            GstStructure *extras = gst_structure_empty_new("extras");
			for(p = extra_headers.c_str(); *p != '\0'; p++)
			{
				len = strlen(p);
				strncpy(header, p, len);
				p = strchr(p, ',');
				if(p != NULL)
				{
					len2 = strlen(p);
					len1 = len-len2;
					header[len1] = '\0';
				}

				if (p == NULL)
					header[len]='\0';

				sscanf(header, "%s %s", &head, &value);
				g_print("%s %s\n",head,value);
				memset(&headerValue, 0, sizeof(GValue));
				g_value_init(&headerValue, G_TYPE_STRING);
				g_value_set_string(&headerValue,value);
				gst_structure_set_value(extras, head, &headerValue);

				if (p == NULL)
					break;
			}

			if (gst_structure_n_fields(extras) > 0)
				g_object_set(G_OBJECT(source), "extra-headers", extras, NULL);

            gst_structure_free(extras);
		}

		gst_object_unref(source);

    // NOTE: code assumes souphttpsrc, but written so anything with "extra-headers"
    // should be functional.
    }
}

void eServiceMP4::got_location (GstBin *bin, GstElement *element, gpointer user_data) {

    eServiceMP4 *_this = (eServiceMP4*)user_data;
	if (_this)
	{
	    g_object_get (G_OBJECT (element), "temp-location", &(_this->m_downloadInfo.downloadPath), NULL);
	    eDebug("ServiceMP4:: Download location is %s",_this->m_downloadInfo.downloadPath.c_str());
	    /* set download path */
	    _this->m_download_poll_timer->start(1000,false);
	    _this->m_event((iPlayableService*)_this, evUser+20);
	}
}

PyObject *eServiceMP4::getDownloadInfo()
{
	ePyObject tuple = PyTuple_New(5);
	PyTuple_SET_ITEM(tuple, 0, PyInt_FromLong(m_downloadInfo.downloading));
	PyTuple_SET_ITEM(tuple, 1, PyString_FromString(m_downloadInfo.downloadPath.c_str()));
	PyTuple_SET_ITEM(tuple, 2, PyInt_FromLong(m_downloadInfo.downloadPercent));
	return tuple;
}

void eServiceMP4::updateDownloadStatus() {
    GstQuery *query;
    gboolean result;
    gint percent;
    gboolean busy;

    if (!m_gst_playbin)
    {
		m_download_poll_timer->stop();
		m_downloadInfo.downloading = 0;
		return;
    }

    if (m_downloadInfo.downloading==0)
        return;

    query = gst_query_new_buffering (GST_FORMAT_PERCENT);
    result = gst_element_query (m_gst_playbin, query);

    if (result)
    {
        GstFormat format = GST_FORMAT_TIME;
        gint64 position = 0, duration = 0;
        gint64 start=0,stop=0;

        gst_query_parse_buffering_range(query,0,&start,&stop,0);
        //g_print("Start: %lu, End: %lu, Estimated total: %lu",start,stop,total);
        m_downloadInfo.downloadPercent = 100.0 * stop / GST_FORMAT_PERCENT_MAX;
        if (m_downloadInfo.downloadPercent==100)
        {
            m_downloadInfo.downloading = 1;
            m_download_poll_timer->stop();
            eDebug("eServiceMP4::Download finished");

            /* download finished */
            m_event((iPlayableService*)this, evUser+21);
        }
    }
}

void eServiceMP4::handleElementAdded(GstBin *bin, GstElement *element, gpointer user_data)
{
	eServiceMP4 *_this = (eServiceMP4*)user_data;
	if (_this)
	{
		gchar *elementname = gst_element_get_name(element);

		if (g_str_has_prefix(elementname, "queue2"))
		{
		    /*we are downloading full length of file*/
		    if(_this->m_download_mode)
		    {
		        g_object_set(G_OBJECT(element), "temp-template", _this->m_download_path.c_str(), NULL);
		        eDebug("Setting download path to %s",_this->m_download_path.c_str());
		        //g_object_set(G_OBJECT(element), "temp-remove", FALSE, NULL);
		    }
		    /*progressive download buffering*/
			else if (_this->m_download_buffer_path != "")
			{
				g_object_set(G_OBJECT(element), "temp-template", _this->m_download_buffer_path.c_str(), NULL);
			}
			//else
			//{
			//	g_object_set(G_OBJECT(element), "temp-template", NULL, NULL);
			//}
		}
		else if (g_str_has_prefix(elementname, "uridecodebin"))
		{
			/*
			 * Listen for queue2 element added to uridecodebin/decodebin2 as well.
			 * Ignore other bins since they may have unrelated queues
			 */
				g_signal_connect(element, "element-added", G_CALLBACK(handleElementAdded), user_data);
		}
		g_free(elementname);
	}
}

audiotype_t eServiceMP4::gstCheckAudioPad(GstStructure* structure)
{
	if (!structure)
		return atUnknown;

	if ( gst_structure_has_name (structure, "audio/mpeg"))
	{
		gint mpegversion, layer = -1;
		if (!gst_structure_get_int (structure, "mpegversion", &mpegversion))
			return atUnknown;

		switch (mpegversion) {
			case 1:
				{
					gst_structure_get_int (structure, "layer", &layer);
					if ( layer == 3 )
						return atMP3;
					else
						return atMPEG;
					break;
				}
			case 2:
				return atAAC;
			case 4:
				return atAAC;
			default:
				return atUnknown;
		}
	}

	else if ( gst_structure_has_name (structure, "audio/x-ac3") || gst_structure_has_name (structure, "audio/ac3") )
		return atAC3;
	else if ( gst_structure_has_name (structure, "audio/x-dts") || gst_structure_has_name (structure, "audio/dts") )
		return atDTS;
	else if ( gst_structure_has_name (structure, "audio/x-raw-int") )
		return atPCM;

	return atUnknown;
}

void eServiceMP4::gstPoll(ePtr<GstMessageContainer> const &msg)
{
	switch (msg->getType())
	{
		case 1:
		{
			GstMessage *gstmessage = *((GstMessageContainer*)msg);
			if (gstmessage)
			{
				gstBusCall(gstmessage);
			}
			break;
		}
		case 2:
		{
			GstBuffer *buffer = *((GstMessageContainer*)msg);
			if (buffer)
			{
				pullSubtitle(buffer);
			}
			break;
		}
		case 3:
		{
			GstPad *pad = *((GstMessageContainer*)msg);
			gstTextpadHasCAPS_synced(pad);
			break;
		}
	}
}

eAutoInitPtr<eServiceFactoryMP4> init_eServiceFactoryMP4(eAutoInitNumbers::service+1, "eServiceFactoryMP4");

void eServiceMP4::gstCBsubtitleAvail(GstElement *subsink, GstBuffer *buffer, gpointer user_data)
{
	eServiceMP4 *_this = (eServiceMP4*)user_data;
	if (_this->m_currentSubtitleStream < 0)
	{
		if (buffer) gst_buffer_unref(buffer);
		return;
	}
#if GST_VERSION_MAJOR < 1
	guint8 *label = GST_BUFFER_DATA(buffer);
#else
	guint8 label[32] = {0};
	gst_buffer_extract(buffer, 0, label, sizeof(label));
#endif
	eDebug("gstCBsubtitleAvail: %s", (const char*)label);
	_this->m_pump.send(new GstMessageContainer(2, NULL, NULL, buffer));
}

void eServiceMP4::gstTextpadHasCAPS(GstPad *pad, GParamSpec * unused, gpointer user_data)
{
	eServiceMP4 *_this = (eServiceMP4*)user_data;

	gst_object_ref (pad);

	_this->m_pump.send(new GstMessageContainer(3, NULL, pad, NULL));
}

void eServiceMP4::gstTextpadHasCAPS_synced(GstPad *pad)
{
	GstCaps *caps = NULL;

	g_object_get (G_OBJECT (pad), "caps", &caps, NULL);

	if (caps)
	{
		subtitleStream subs;

		eDebug("gstTextpadHasCAPS:: signal::caps = %s", gst_caps_to_string(caps));
//		eDebug("gstGhostpadHasCAPS_synced %p %d", pad, m_subtitleStreams.size());

		if (m_currentSubtitleStream >= 0 && m_currentSubtitleStream < (int)m_subtitleStreams.size())
			subs = m_subtitleStreams[m_currentSubtitleStream];
		else {
			subs.type = stUnknown;
			subs.pad = pad;
		}

		if ( subs.type == stUnknown )
		{
			GstTagList *tags = NULL;
			gchar *g_lang = NULL;
			g_signal_emit_by_name (m_gst_playbin, "get-text-tags", m_currentSubtitleStream, &tags);

			subs.language_code = "und";
			subs.type = getSubtitleType(pad);
#if GST_VERSION_MAJOR < 1
			if (tags && gst_is_tag_list(tags))
#else
			if (tags && GST_IS_TAG_LIST(tags))
#endif
			{
				if (gst_tag_list_get_string(tags, GST_TAG_LANGUAGE_CODE, &g_lang))
				{
					subs.language_code = std::string(g_lang);
					g_free(g_lang);
				}
			}

			if (m_currentSubtitleStream >= 0 && m_currentSubtitleStream < (int)m_subtitleStreams.size())
				m_subtitleStreams[m_currentSubtitleStream] = subs;
			else
				m_subtitleStreams.push_back(subs);
		}

//		eDebug("gstGhostpadHasCAPS:: m_gst_prev_subtitle_caps=%s equal=%i",gst_caps_to_string(m_gst_prev_subtitle_caps),gst_caps_is_equal(m_gst_prev_subtitle_caps, caps));

		gst_caps_unref (caps);
	}
}

void eServiceMP4::pullSubtitle(GstBuffer *buffer)
{
	if (buffer && m_currentSubtitleStream >= 0 && m_currentSubtitleStream < (int)m_subtitleStreams.size())
	{
		gint64 buf_pos = GST_BUFFER_TIMESTAMP(buffer);
		gint64 duration_ns = GST_BUFFER_DURATION(buffer);
#if GST_VERSION_MAJOR < 1
		size_t len = GST_BUFFER_SIZE(buffer);
#else
		size_t len = gst_buffer_get_size(buffer);
#endif
		eDebug("pullSubtitle m_subtitleStreams[m_currentSubtitleStream].type=%i",m_subtitleStreams[m_currentSubtitleStream].type);

		if ( m_subtitleStreams[m_currentSubtitleStream].type )
		{
			if ( m_subtitleStreams[m_currentSubtitleStream].type < stVOB )
			{
				unsigned char line[len+1];
				SubtitlePage page;
#if GST_VERSION_MAJOR < 1
				memcpy(line, GST_BUFFER_DATA(buffer), len);
#else
				gst_buffer_extract(buffer, 0, line, len);
#endif
				line[len] = 0;
				eDebug("got new text subtitle @ buf_pos = %lld ns (in pts=%lld): '%s' ", buf_pos, buf_pos/11111, line);
				gRGB rgbcol(0xD0,0xD0,0xD0);
				page.type = SubtitlePage::Pango;
				page.pango_page.m_elements.push_back(ePangoSubtitlePageElement(rgbcol, (const char*)line));
				page.pango_page.m_show_pts = buf_pos / 11111L;
				page.pango_page.m_timeout = duration_ns / 1000000;
				m_subtitle_pages.push_back(page);
				if (m_subtitle_pages.size()==1)
					pushSubtitles();
			}
			else
			{
				eDebug("unsupported subpicture... ignoring");
			}
		}
	}
}

void eServiceMP4::pushSubtitles()
{
	while ( !m_subtitle_pages.empty() )
	{
		SubtitlePage &frontpage = m_subtitle_pages.front();
		pts_t running_pts = 0;
		gint64 diff_ms = 0;
		gint64 show_pts = 0;

		if (getPlayPosition(running_pts) < 0)
		{
			m_decoder_time_valid_state = 0;
		}
		if (m_decoder_time_valid_state < 4) {
			++m_decoder_time_valid_state;
			if (m_prev_decoder_time == running_pts)
				m_decoder_time_valid_state = 0;
			if (m_decoder_time_valid_state < 4) {
				m_subtitle_sync_timer->start(50, true);
				m_prev_decoder_time = running_pts;
				break;
			}
		}

		if (frontpage.type == SubtitlePage::Pango)
			show_pts = frontpage.pango_page.m_show_pts;

		diff_ms = ( show_pts - running_pts ) / 90;
		eDebug("check subtitle: decoder: %lld, show_pts: %lld, diff: %lld ms", running_pts/90, show_pts/90, diff_ms);

		if ( diff_ms < -100 )
		{
			eDebug("subtitle too late... drop");
			m_subtitle_pages.pop_front();
		}
		else if ( diff_ms > 20 )
		{
			eDebug("start timer, %lldms", diff_ms);
			m_subtitle_sync_timer->start(diff_ms, true);
			break;
		}
		else // immediate show
		{
			if ( m_subtitle_widget )
			{
				eDebug("show!\n");
				if ( frontpage.type == SubtitlePage::Pango)
					m_subtitle_widget->setPage(frontpage.pango_page);
				m_subtitle_widget->show();
			}
			m_subtitle_pages.pop_front();
		}
	}
}

RESULT eServiceMP4::enableSubtitles(eWidget *parent, ePyObject tuple)
{
	ePyObject entry;
	int tuplesize = PyTuple_Size(tuple);
	int pid;

	if (!PyTuple_Check(tuple))
		goto error_out;
	if (tuplesize < 1)
		goto error_out;
	entry = PyTuple_GET_ITEM(tuple, 1);
	if (!PyInt_Check(entry))
		goto error_out;
	pid = PyInt_AsLong(entry);

	if (m_currentSubtitleStream != pid)
	{
		g_object_set (G_OBJECT (m_gst_playbin), "current-text", -1, NULL);
		m_subtitle_pages.clear();
		m_prev_decoder_time = -1;
		m_decoder_time_valid_state = 0;
		m_currentSubtitleStream = pid;
		m_cachedSubtitleStream = m_currentSubtitleStream;
		g_object_set (G_OBJECT (m_gst_playbin), "current-text", m_currentSubtitleStream, NULL);

		m_subtitle_widget = 0;
		m_subtitle_widget = new eSubtitleWidget(parent);
		m_subtitle_widget->resize(parent->size()); /* full size */

		eDebug ("eServiceMP4::switched to subtitle stream %i", m_currentSubtitleStream);

#ifdef GSTREAMER_SUBTITLE_SYNC_MODE_BUG
		/*
		 * when we're running the subsink in sync=false mode,
		 * we have to force a seek, before the new subtitle stream will start
		 */
		seekRelative(-1, 90000);
#endif
	}

	return 0;

error_out:
	eDebug("eServiceMP4::enableSubtitles needs a tuple as 2nd argument!\n"
		"for gst subtitles (2, subtitle_stream_count, subtitle_type)");
	return -1;
}

RESULT eServiceMP4::disableSubtitles(eWidget *parent)
{
	eDebug("eServiceMP4::disableSubtitles");
	m_currentSubtitleStream = -1;
	m_cachedSubtitleStream = m_currentSubtitleStream;
	g_object_set (G_OBJECT (m_gst_playbin), "current-text", m_currentSubtitleStream, NULL);
	m_subtitle_pages.clear();
	m_prev_decoder_time = -1;
	m_decoder_time_valid_state = 0;
	delete m_subtitle_widget;
	m_subtitle_widget = 0;
	return 0;
}

PyObject *eServiceMP4::getCachedSubtitle()
{
	if (m_cachedSubtitleStream >= 0 && m_cachedSubtitleStream < (int)m_subtitleStreams.size())
	{
		ePyObject tuple = PyTuple_New(4);
		PyTuple_SET_ITEM(tuple, 0, PyInt_FromLong(2));
		PyTuple_SET_ITEM(tuple, 1, PyInt_FromLong(m_cachedSubtitleStream));
		PyTuple_SET_ITEM(tuple, 2, PyInt_FromLong(int(m_subtitleStreams[m_cachedSubtitleStream].type)));
		PyTuple_SET_ITEM(tuple, 3, PyInt_FromLong(0));
		return tuple;
	}
	Py_RETURN_NONE;
}

PyObject *eServiceMP4::getSubtitleList()
{
// 	eDebug("eServiceMP4::getSubtitleList");
	ePyObject l = PyList_New(0);
	int stream_idx = 0;

	for (std::vector<subtitleStream>::iterator IterSubtitleStream(m_subtitleStreams.begin()); IterSubtitleStream != m_subtitleStreams.end(); ++IterSubtitleStream)
	{
		subtype_t type = IterSubtitleStream->type;
		switch(type)
		{
		case stUnknown:
		case stVOB:
		case stPGS:
			break;
		default:
		{
			ePyObject tuple = PyTuple_New(5);
//			eDebug("eServiceMP4::getSubtitleList idx=%i type=%i, code=%s", stream_idx, int(type), (IterSubtitleStream->language_code).c_str());
			PyTuple_SET_ITEM(tuple, 0, PyInt_FromLong(2));
			PyTuple_SET_ITEM(tuple, 1, PyInt_FromLong(stream_idx));
			PyTuple_SET_ITEM(tuple, 2, PyInt_FromLong(int(type)));
			PyTuple_SET_ITEM(tuple, 3, PyInt_FromLong(0));
			PyTuple_SET_ITEM(tuple, 4, PyString_FromString((IterSubtitleStream->language_code).c_str()));
			PyList_Append(l, tuple);
			Py_DECREF(tuple);
		}
		}
		stream_idx++;
	}
	eDebug("eServiceMP4::getSubtitleList finished");
	return l;
}

RESULT eServiceMP4::streamed(ePtr<iStreamedService> &ptr)
{
	ptr = this;
	return 0;
}

PyObject *eServiceMP4::getBufferCharge()
{
	ePyObject tuple = PyTuple_New(5);
	PyTuple_SET_ITEM(tuple, 0, PyInt_FromLong(m_bufferInfo.bufferPercent));
	PyTuple_SET_ITEM(tuple, 1, PyInt_FromLong(m_bufferInfo.avgInRate));
	PyTuple_SET_ITEM(tuple, 2, PyInt_FromLong(m_bufferInfo.avgOutRate));
	PyTuple_SET_ITEM(tuple, 3, PyInt_FromLong(m_bufferInfo.bufferingLeft));
	PyTuple_SET_ITEM(tuple, 4, PyInt_FromLong(m_buffer_size));
	return tuple;
}

int eServiceMP4::setBufferSize(int size)
{
	m_buffer_size = size;
	g_object_set (G_OBJECT (m_gst_playbin), "buffer-size", m_buffer_size, NULL);
	return 0;
}

int eServiceMP4::getAC3Delay()
{
	return ac3_delay;
}

int eServiceMP4::getPCMDelay()
{
	return pcm_delay;
}

void eServiceMP4::setAC3Delay(int delay)
{
	ac3_delay = delay;
	if (!m_gst_playbin || m_state != stRunning)
		return;
	else
	{
		int config_delay_int = delay;

		/*
		 * NOTE: We only look for dvbmediasinks.
		 * If either the video or audio sink is of a different type,
		 * we have no chance to get them synced anyway.
		 */
		if (videoSink)
		{
			std::string config_delay;
			if(ePythonConfigQuery::getConfigValue("config.av.generalAC3delay", config_delay) == 0)
				config_delay_int += atoi(config_delay.c_str());
		}
		else
		{
			eDebug("dont apply ac3 delay when no video is running!");
			config_delay_int = 0;
		}

		if (audioSink)
		{
			eTSMPEGDecoder::setHwAC3Delay(config_delay_int);
		}
	}
}

void eServiceMP4::setPCMDelay(int delay)
{
	pcm_delay = delay;
	if (!m_gst_playbin || m_state != stRunning)
		return;
	else
	{
		int config_delay_int = delay;

		/*
		 * NOTE: We only look for dvbmediasinks.
		 * If either the video or audio sink is of a different type,
		 * we have no chance to get them synced anyway.
		 */
		if (videoSink)
		{
			std::string config_delay;
			if(ePythonConfigQuery::getConfigValue("config.av.generalPCMdelay", config_delay) == 0)
				config_delay_int += atoi(config_delay.c_str());
		}
		else
		{
			eDebug("dont apply pcm delay when no video is running!");
			config_delay_int = 0;
		}

		if (audioSink)
		{
			eTSMPEGDecoder::setHwPCMDelay(config_delay_int);
		}
	}
}

PyMODINIT_FUNC
initservicemp4(void)
{
        Py_InitModule("servicemp4", NULL);
}
