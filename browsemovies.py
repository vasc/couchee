import pymongo
from sys import stdin
import re
import urllib

def main():
    db = pymongo.Connection().usenet
    print "Search movies without id:"
    s = stdin.readline()
    nzbs = [nzb for nzb in db.nzbs.find({'rlsname': re.compile('%s' % s.rstrip(), re.I)})]
    for i in range(0, len(nzbs)):
        print str(i) + ':', nzbs[i]['rlsname']
        
    #print
    while True:
        print 'Display: p [num] or "exit"'
        s = stdin.readline()
        if s == 'exit\n': return
        m = re.match(r"^p\s+(\d+)\n", s)
        m2 = re.amtch(r"^rm\s+(\d+)\n", s)
        if m:
            i = int(m.group(1))
            nzb = nzbs[i]
            print nzb
        elif m2:
            print 'not implemented yet ;)'
            


if __name__ == '__main__':
    main()
