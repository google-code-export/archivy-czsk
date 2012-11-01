# -*- coding: utf-8 -*-
#------------------------------------------------------------
#
# Modify: 2011-08-15, by Ivo Brhel
#
#------------------------------------------------------------

import re, sys, os
import urlparse, urllib, urllib2


_UserAgent_ =  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)'
novamov_url="http://www.novamov.com/api/player.api.php"

def getURL(url):
	urlhq=""
	req = urllib2.Request(url)
   	req.add_header('User-Agent',_UserAgent_)
    	response = urllib2.urlopen(req)
    	link=response.read()
	#
	match=re.compile('flashvars.advURL=\"(.+?)\".*').findall(link)
	if match[0] != "0":
		# src='http://embed.novamov.com/embed.php?width=600&#038;height=480&#038;v=vje17kmmztnbb&#038;px=1'
		req = urllib2.Request(match[0])
   		req.add_header('User-Agent',_UserAgent_)
    		response = urllib2.urlopen(req)
    		link=response.read()
    	match=re.compile('flashvars.file=\"(.+?)\".*').findall(link)
	file=match[0]
    	match=re.compile('flashvars.filekey=\"(.+?)\".*').findall(link)
	filekey=match[0]
	#
	#http://www.novamov.com/api/player.api.php?key=fc55ea26c57ac86c74918540a163a917&pass=undefined&file=7cv2x4wtrqzmi&user=undefined&codes=1
	urlhq=novamov_url+"?key="+filekey+"&pass=undefined&file="+file+"&user=undefined&codes=1"
	req = urllib2.Request(urlhq)
   	req.add_header('User-Agent',_UserAgent_)
    	response = urllib2.urlopen(req)
    	link=response.read()
    	response.close()
    	#	
    	#match=re.compile('url=(.+?)&title=.*').findall(link)
    	match=re.compile('url=http://(.+?)&title=.+?').findall(link)
	#print "{NOVAMOV MATCH2:"
	#print match
	urlhq='http://'+match[0]

	return urlhq
