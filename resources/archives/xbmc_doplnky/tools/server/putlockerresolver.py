# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import re
try:
    from Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools import util
except ImportError:
    from resources.archives.xbmc_doplnky.tools import util
__name__ = 'putlocker'
def supports(url):
	return not _regex(url) == None


				
def get_host_and_id(url):
        r = re.search('//(.+?)/(?:file|embed)/([0-9A-Z]+)', url)
        if r:
            return r.groups()
        else:
            return False

def get_host(url):
	host,media_id=get_host_and_id(url)
        if 'putlocker' in host:
            host = 'www.putlocker.com'
        else:
            host = 'www.sockshare.com'
        return 'http://%s/file/%s' % (host, media_id)
				
				
# returns the steam url
def url(url):
	if not _regex(url) == None:
		util.init_urllib()
		web_url = get_host(url)
		data = util.substr(util.request(web_url),'<form method=\"post','</form>')
		# need to POST input called confirm to url, fields: hash, confirm found in request'
		m = re.search('<input(.+?)value=\"(?P<hash>[^\"]+)(.+?)name=\"hash\"(.+?)<input name=\"confirm\"(.+?)value=\"(?P<confirm>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
		if not m == None:
			data = util.post(web_url,{'confirm':m.group('confirm'),'hash':m.group('hash')})
			# now, we've got (flow)player
			data = util.substr(data,'flowplayer(','</script>')
			print data
			n = re.search('playlist\: \'(?P<pls>[^\']+)',data,re.IGNORECASE | re.DOTALL)
			if not n == None:
				# now download playlist
				xml = util.request('http://www.putlocker.com'+n.group('pls'))
				return [re.search('url=\"([^\"]+)\" type=\"video',xml,re.IGNORECASE | re.DOTALL).group(1)]
				
				
def _regex(url):
	return re.search('(www\.)putlocker.com/(.+?)',url,re.IGNORECASE | re.DOTALL)
