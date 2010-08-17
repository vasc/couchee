import pymongo
import urllib
import urllib2

for nzb in pymongo.Connection().usenet.nzbs.find({'stage': 3, 'tags': '#a.b.moovee@EFNet'}):
    data = urllib.urlencode([('rlsname', nzb['rlsname']), ('nzblink', 'nzblink'), ('imdblink', nzb['link']), ('nzbdate',str(nzb['date']))])
    print urllib2.urlopen('http://localhost:8080/upload', data)
