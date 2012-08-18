# -*- coding: utf-8 -*-
# Author: Ricardo Garcia Gonzalez
# Author: Danny Colligan
# Author: Benjamin Johnson
# Author: Vasyl' Vavrychuk
# Author: Witold Baryluk
# Author: Paweł Paprota
# Author: Gergely Imreh
# License: Public domain code
#
# Modify: 2011-08-17, Ivo Brhel
#

import urllib2,urllib,re
import os
import string
from urlparse import parse_qs, parse_qsl




std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100720 Firefox/3.6.7',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
	}


_VALID_URL = r'^((?:https?://)?(?:youtu\.be/|(?:\w+\.)?youtube(?:-nocookie)?\.com/)(?:(?:(?:v|embed|e)/)|(?:(?:watch(?:_popup)?(?:\.php)?)?(?:\?|#!?)(?:.+&)?v=)))?([0-9A-Za-z_-]+)(?(1).+)?$'

_LANG_URL = r'http://www.youtube.com/?hl=en&persist_hl=1&gl=US&persist_gl=1&opt_out_ackd=1'
# Listed in order of quality
_available_formats = ['38', '37', '22', '45', '35', '34', '43', '18', '6', '5', '17', '13']
_video_extensions = {
	'13': '3gp',
	'17': 'mp4',
	'18': 'mp4',
	'22': 'mp4',
	'37': 'mp4',
	'38': 'video', # You actually don't know if this will be MOV, AVI or whatever
	'43': 'webm',
	'45': 'webm',
}

def report_video_webpage_download( video_id):
	"""Report attempt to download video webpage."""
	print(u'[youtube] %s: Downloading video webpage' % video_id)
	
def report_video_info_webpage_download( video_id):
	"""Report attempt to download video info webpage."""
	print(u'[youtube] %s: Downloading video info webpage' % video_id)
	
	


def getURL(url):
	# Extract video id from URL
	mobj = re.match(_VALID_URL, url)
	if mobj is None:
		print(u'ERROR: invalid URL: %s' % url)
		return
	video_id = mobj.group(2)

	# Get video webpage
	report_video_webpage_download(video_id)
	request = urllib2.Request('http://www.youtube.com/watch?v=%s&gl=US&hl=en&amp;has_verified=1' % video_id)
	try:
		video_webpage = urllib2.urlopen(request).read()
	except  err:
		print(u'ERROR: unable to download video webpage: %s' % str(err))
		return

	# Attempt to extract SWF player URL
	mobj = re.search(r'swfConfig.*?"(http:\\/\\/.*?watch.*?-.*?\.swf)"', video_webpage)
	if mobj is not None:
		player_url = re.sub(r'\\(.)', r'\1', mobj.group(1))
	else:
		player_url = None

	# Get video info
	#report_video_info_webpage_download(video_id)
	for el_type in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
		video_info_url = ('http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en'
				   % (video_id, el_type))
		request = urllib2.Request(video_info_url)
		try:
			video_info_webpage = urllib2.urlopen(request).read()
			video_info = parse_qs(video_info_webpage)
			if 'token' in video_info:
				break
		except (urllib2.URLError, httplib.HTTPException, socket.error), err:
			print(u'ERROR: unable to download video info webpage: %s' % str(err))
			return
	if 'token' not in video_info:
		if 'reason' in video_info:
			print(u'ERROR: YouTube said: %s' % video_info['reason'][0].decode('utf-8'))
		else:
			print(u'ERROR: "token" parameter not in video info for unknown reason')
		return

	
	if 'url_encoded_fmt_stream_map' in video_info and len(video_info['url_encoded_fmt_stream_map']) >= 1:
		url_data_strs = video_info['url_encoded_fmt_stream_map'][0].split(',')
		url_data = [dict(pairStr.split('=') for pairStr in uds.split('&')) for uds in url_data_strs]
		url_map = dict((ud['itag'], urllib.unquote(ud['url'])) for ud in url_data)
		#format_limit = params.get('format_limit', None)
		format_list = _available_formats
		existing_formats = [x for x in format_list if x in url_map]
		if len(existing_formats) == 0:
			print(u'ERROR: no known formats available for video')
			return
		#if req_format is None:
		video_url_list = [(existing_formats[0], url_map[existing_formats[0]])] # Best quality
		#elif req_format == '-1':
		#	video_url_list = [(f, url_map[f]) for f in existing_formats] # All formats
		#else:
		#	# Specific format
		#	if req_format not in url_map:
		#		print(u'ERROR: requested format not available')
		#		return
		#	video_url_list = [(req_format, url_map[req_format])] # Specific format

	elif 'conn' in video_info and video_info['conn'][0].startswith('rtmp'):
		#self.report_rtmp_download()
		video_url_list = [(None, video_info['conn'][0])]

	else:
		print(u'ERROR: no fmt_url_map or conn information found in video info')
		return


	
	
	for format_param, video_real_url in video_url_list:
		# At this point we have a new video
		#self._downloader.increment_downloads()
		return video_real_url.decode('utf-8')

		
