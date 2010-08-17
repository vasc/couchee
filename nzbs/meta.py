import re
import pymongo
from nntplib import NNTP
from lxml import objectify
from lxml.etree import XMLSyntaxError
from nntplib import NNTPTemporaryError
import gzip
import os
from download import download_articles


def tv_meta_info(rlsname):
    #regular
    m1 = re.search(r'^(?P<show>(\w+\.)+)s(?P<s>\d?\d)\.?e(?P<e>\d\d)(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #regular with x
    m2 = re.search(r'^(?P<show>(\w+\.)+)s(?P<s>\d?\d)x(?P<e>\d\d)(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #by day
    m3 = re.search(r'^(\w+\.)+(\d\d)?\d\d\.\d\d\.\d\d(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #fov style
    m4 = re.search(r'^(?P<show>(\w+_)*\w+)\.(?P<s>\d?\d)x(?P<e>\d\d)\.(\w+_)*\w+(\.\w+)*-(\w+\.)*\w+$', rlsname, re.I)
    #multiple episode
    m5 = re.search(r'^(\w+\.)+s\d\de\d\d-?e?\d\d(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #disc style
    m6 = re.search(r'^(\w+\.)+s\d\dd\d?\d(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #full season
    m7 = re.search(r'^(\w+\.)+s\d\d(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    m = None
    if m4: m = m4
    if m2: m = m2
    if m1: m = m1
    
    if m:
        #print "%s S%sE%s" % (re.sub('[\._]', ' ', m.group('show')), m.group('s'), m.group('e'))
        pass
    else: print rlsname 
    return m1 or m2 or m3 or m4 or m5 or m6 or m7

def meta_nzbs():
    db = pymongo.Connection().usenet
    count = {}
    count[True] = 0
    count[False] = 0
    for nzb in db.nzbs.find({'stage': 2}):
        r = bool(tv_meta_info(nzb['rlsname']))
        count[r] += 1
    print count
        
   
def id_movies():
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'stage': 2, 'tags': '#a.b.moovee@EFNet'}):
        if '430 nfo' in nzb['stages']: continue #print '430', nzb['rlsname']; 
        if 'no imdb' in nzb['stages']: continue #print 'No IMDB', nzb['rlsname']; 
        if 'no nfo' in nzb['stages']: continue #print 'No IMDB', nzb['rlsname']; 
        folder = db.config.find_one({'type': 'folder', 'category': 'moovee'})['folder']         
        filename = nzb['file']
        nntp = NNTP('eu.news.astraweb.com', user='vasc', password='otherplace')
        try:
            root = objectify.parse(gzip.open(os.path.join(folder, filename), 'rb')).getroot()
            for f in root.getchildren():
                if f.tag == '{http://www.newzbin.com/DTD/2003/nzb}file':
                    if re.search("\.nfo[\'\"\s\)\]]", f.attrib['subject']):
                        articles = [{'msgid': '<'+str(a)+'>'} for a in f.segments.getchildren() if a.tag == '{http://www.newzbin.com/DTD/2003/nzb}segment']
                        #print articles
                        nfo_file = download_articles(nntp, articles)
                        
                        #m = re.search(r'http://[^\s\n]*\s', nfo_file)
                        #if m: print m.group(0)
                        #else: print nzb['file']
                        
                        m = re.search('tt(\d{7,})', nfo_file)
                        if not m: m = re.search(r'Title\?(\d{7,})', nfo_file, flags=re.I)
                        if m:
                            nzb['link'] = 'http://www.imdb.com/title/tt' + m.group(1) + '/'
                            nzb['movieid'] = 'tt' + m.group(1)
                            nzb['stage'] = 3
                            nzb['stages'].append('movieid')
                            db.nzbs.save(nzb)
                        
                            print 'ID', nzb['rlsname'], 'as http://www.imdb.com/title/tt' + m.group(1) + '/'
                            logging.info('ID ' + nzb['rlsname'] + ' as http://www.imdb.com/title/tt' + m.group(1) + '/')
                        else: 
                            print 'Unable to identify', nzb['rlsname']
                            nzb['error'] = {'value': 422, 'msg': '', 'help': 'nfo does not contain identifiable imdb link'}
                            nzb['stages'].append('no imdb')
                            db.nzbs.save(nzb) 
                        return
                        #else: print nzb['file']
            print 'No nfo in nzb', nzb['rlsname']
            nzb['error'] = {'value': 423, 'msg': '', 'help': 'nzb file does not contain nfo'}
            nzb['stages'].append('no nfo')
            db.nzbs.save(nzb)               
        except XMLSyntaxError as e:
            nzb['error'] = {'value': 420, 'msg': str(e), 'help': 'nzb file is not valid xml'}
            nzb['stage'] = 400
            nzb['stages'].append('error')
            db.nzbs.save(nzb)
        except NNTPTemporaryError as e:
            if e.startswith('430'):
                nzb['error'] = {'value': 421, 'msg': str(e), 'help': 'nfo article is not available in server, waiting for a backup server'}
                nzb['stages'].append('430 nfo')
                db.nzbs.save(nzb)
            print articles, e
        #except Exception:
        #     print 'error'
        #     continue
        #break
