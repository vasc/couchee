import pymongo
from sys import stdin
import re
import urllib

def main():
    db = pymongo.Connection().usenet
    print "Search movies without id:"
    s = stdin.readline()
    nzbs = [nzb for nzb in db.nzbs.find({'stages.movieid': {'$ne': True}, 'stages.uploaded': True, 'tags': '#a.b.moovee@EFNet', 'rlsname': re.compile('%s' % s.rstrip(), re.I)})]
    for i in range(0, len(nzbs)):
        if 'error' in nzbs[i] and not nzbs[i]['error']['value'] in [421, 422, 423]: print 'ERROR', nzbs[i]['rlsname']; continue
        print str(i) + ':', nzbs[i]['rlsname']
        
    print
    while True:
        print 'Id movie: [num] [imdbid (ex. tt0123456)] or "exit"'
        s = stdin.readline()
        if s == 'exit\n': return
        m = re.match(r"(\d+)\s(tt\d{7})\n", s)
        m2 = re.match(r"^p\s+(\d+)\n", s)
        if m:
            i = int(m.group(1))
            nzb = nzbs[i]
            print 'Ided', nzb['rlsname'], 'as', 'http://www.imdb.com/title/' + m.group(2) + '/'
            print 'Are you sure (y/N)?'
            s = stdin.readline()
            if not s or not s[0] == 'y': continue
            del nzb['error']
            del nzb['stages']['error']
            nzb['link'] = 'http://www.imdb.com/title/' + m.group(2) + '/'
            nzb['movieid'] = m.group(2)
            nzb['stage'] = 3
            nzb['stages']['movieid'] = True
            db.nzbs.save(nzb)
            #print nzb
        elif m2:
            i = int(m2.group(1))
            nzb = nzbs[i]
            print nzb
            


if __name__ == '__main__':
    main()
