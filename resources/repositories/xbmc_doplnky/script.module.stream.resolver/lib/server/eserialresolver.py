# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import re
__name__='eserial'
def supports(url):
    return not _regex(url) == None

# returns the steam url
def resolve(url):
    m = _regex(url)
    if m:
        print 'yes'
        return [{'url':m.group('url')}]

def _regex(url):
    return re.search('eserial\.cz/video\.php\?file=(?P<url>.+?)$',url,re.IGNORECASE | re.DOTALL)

