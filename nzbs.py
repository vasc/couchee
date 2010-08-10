import pynotify
import pymongo
import re
from nntplib import NNTP
import yencdecode
import os
import multiprocessing as mp
import time
import gzip
import uuid
from datetime import datetime, timedelta
import logging


def date_nzbs():
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'date': None}):
        if not 'date' in nzb:
            if 'rlsname' in nzb: id = 'rlsname'
            else: id = '_id'
            date = nzb['articles'][0]['date']
            tzd = re.search("[-+](\d\d)(\d\d)$", date)
            d = parse_date(date, "%d %b %Y %H:%M:%S %Z")
            if not d:
                d = parse_date(date, "%a, %d %b %Y %H:%M:%S %Z")
            if not d and tzd:
                d = parse_date(date[:-6], "%a, %d %b %Y %H:%M:%S")
                td = timedelta(hours=int(tzd.group(1)), minutes=int(tzd.group(2)))
                if date[-5] == '+': d = d - td
                else: d = d + td
                print '%s => %s' % (date, d)
            if not d:
                logging.error("Unable to parse date: %s from %s" % (nzb[id], nzb['date']))
            else:
                nzb['date'] = d
                logging.info("Dated %s: %s" % (nzb[id], nzb['date']))
                db.nzbs.save(nzb)
                    
def parse_date(date, format):
    try:
        d = datetime.strptime(date, format)
    except ValueError:
        d = None
    return d

def organize_nzbs():
    db = pymongo.Connection().usenet
    r = re.compile(r'\((\d+)\\(\d+)\)\s*$')
    for h in db.headers.find():
        m = re.search(r'(.*)\((\d+)\/(\d+)\)\s*$', h['subject'])
        if m:
            c = False
            name = m.group(1)
            part = m.group(2)
            total = m.group(3)
            nzb = db.nzbs.find_one({'_id': name})
            if not nzb:
                c = True
                nzb = {'_id': name,
                       'total': total,
                       'group': h['group'],
                       'articles': [], 
                       'stage': 0
                      }
            article = {'msgid': h['_id'], 'part': part, 'date': h['date']}
            nzb['articles'].append(article)
            db.nzbs.save(nzb)
            if c: s = "Created"
            else: s= "Updated"
            logging.info("%s nzb: %s" % (s, nzb['_id']))
        db.headers.remove({'_id': h['_id']})

def movie_tag(nzb, db):
    m = re.search(r'\s*\[\s*#altbin\s*@\s*EFNet\s*\]\s*-?\s*\[\s*Full\s*\]', nzb['_id'], re.I)
    if nzb['group'] == 'alt.binaries.movies.divx' and m:
        if not 'tags' in nzb: nzb['tags'] = []
        nzb['tags'].append('#altbin@EFNet')
        nzb['stage'] = 1
        db.nzbs.save(nzb)
        logging.info("Tagged %s as '#altbin@EFNet'" % nzb['_id'])

def moovee_tag(nzb, db):
    m = re.search(r'\s*\[\s*FULL\s*\]\s*-?\s*\[\s*#a.b.moovee@EFNet\s*\]\s*-?\s*\[\s*([^\s\]]*)\s*\]', nzb['_id'], re.I)
    if nzb['group'] == 'alt.binaries.moovee' and m:
        nzb['rlsname'] = m.group(1)
        if not 'tags' in nzb: nzb['tags'] = []
        nzb['tags'].append('#a.b.moovee@EFNet')
        nzb['stage'] = 1
        db.nzbs.save(nzb)
        logging.info("Tagged %s as '#a.b.moovee@EFNet'" % nzb['rlsname'])


def tv_tag(nzb, db):
    m = re.search(r'\s*\[\s*FULL\s*\]\s*-?\s*\[\s*#a.b.teevee@EFNet\s*\]\s*-?\s*\[\s*([^\s\]]*)\s*\]', nzb['_id'], re.I)
    if nzb['group'] == 'alt.binaries.teevee' and m:
        nzb['rlsname'] = m.group(1)
        if not 'tags' in nzb: nzb['tags'] = []
        nzb['tags'].append('#a.b.teevee@EFNet')
        nzb['stage'] = 1
        db.nzbs.save(nzb)
        logging.info("Tagged %s as '#a.b.teevee@EFNet'" % nzb['rlsname'])
        
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

def tag_nzbs():
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'stage': 0}):
        #movie_tag(nzb, db)
        tv_tag(nzb, db)
        moovee_tag(nzb, db)

def meta_nzbs():
    db = pymongo.Connection().usenet
    count = {}
    count[True] = 0
    count[False] = 0
    for nzb in db.nzbs.find({'stage': 2}):
        r = bool(tv_meta_info(nzb['rlsname']))
        count[r] += 1
    print count



def download_nzb(nzb_id, count=0):
    try:
        db = pymongo.Connection().usenet
        p = mp.current_process()
        if not 'news' in p.__dict__:
            p.news = NNTP('eu.news.astraweb.com', user='user', password='pass') 
        news = p.news
        nzb = db.nzbs.find_one({'_id': nzb_id})
        nzb['articles'].sort(key=lambda x: int(x['part']))
        nzbfile = ''
        for a in nzb['articles']:
            response, number, msgid, lines = news.body(a['msgid'])
            if not response.startswith('222 '): raise Exception("Error downloading: '%s'" % response)
            #print (response[:10], number, msgid[:10], lines[:10])
            if lines[0] == '': lines = lines[1:]
            info = yencdecode.decode_from_lines(lines)
            nzbfile += open(info['tmpfilename']).read()
            os.remove(info['tmpfilename'])
        filename = uuid.uuid4()
        if 'rlsname' in nzb: filename = nzb['rlsname'] + ".nzb.gz"
        nzb['file'] = filename
        f = gzip.open(os.path.join('nzb', filename), 'wb')
        f.write(nzbfile)
        f.close()
        if 'date' in nzb:
            t = time.mktime(nzb['date'].timetuple())
            os.utime(os.path.join('nzb', nzb['file']), (t, t))

        nzb['stage'] = 2
        #del nzb['articles']
        db.nzbs.save(nzb)
        logging.info("Downloaded %s" % nzb['rlsname'])
        pynotify.Notification("Release", nzb['rlsname']).show()
    except Exception as e:
        #pynotify.Notification("Nzb download error", str(e)).show()
        if nzb: i = nzb['rlsname']
        else: i = nzb_id
        logging.error("Exception '%s' in %s" % (str(e), i))
        if str(e).startswith('430 '):
            nzb['error'] = {'value': 404, 'msg': str(e)}
            nzb['stage'] = 400
            db.nzbs.save(nzb)
        elif str(e).startswith("First line must be start with '=ybegin '"):
            nzb['error'] = {'value': 415, 'msg': str(e)}
            nzb['stage'] = 400
            db.nzbs.save(nzb)
        elif count < 10:
            download_nzb(nzb_id, count+1)
        else:
            p.news = NNTP('eu.news.astraweb.com', user='vasc', password='otherplace') 
            news.quit()
    db.disconnect()    
    #news.quit()
    #q.put(news)

def download_nzbs():      
    p = mp.Pool(10)    
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'stage': 1, 'tags': "#a.b.teevee@EFNet"}):
        if int(nzb['total']) == 1 and len(nzb['articles']) > 1:
            nzb['articles'] = nzb['articles'][:1]
            db.nzbs.save(nzb)
    
        if len(nzb['articles']) == int(nzb['total']):
            p.apply_async(download_nzb, [nzb['_id']])
    p.close()
    p.join()

if __name__ == "__main__":
    meta_nzbs()
