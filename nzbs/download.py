from nntplib import NNTP
import re
import yencdecode
import os
import uuid
import gzip
import logging
import multiprocessing as mp
import pymongo
import time


def download_articles(nntp, articles):
    nzbfile = ''
    for a in articles:
        response, number, msgid, lines = nntp.body(a['msgid'])
        if not response.startswith('222 '): raise Exception("Error downloading: '%s'" % response)
        if lines[0] == '': lines = lines[1:]
        info = yencdecode.decode_from_lines(lines)
        nzbfile += open(info['tmpfilename']).read()
        os.remove(info['tmpfilename'])
    return nzbfile

def get_folder(nzb):
    db = pymongo.Connection().usenet
    folder = db.config.find_one({'type': 'folder', 'category': 'undefined'})['folder'] 
    if 'category' in nzb:
        c = db.config.find_one({'type': 'folder', 'category': nzb['category']})
        if c: folder = c['folder']
    return folder
        


def download_nzb(nzb_id, count=0):
    try:
        db = pymongo.Connection().usenet
        p = mp.current_process()
        if not 'news' in p.__dict__:
            p.news = NNTP('eu.news.astraweb.com', user='vasc', password='otherplace') 
        news = p.news
        nzb = db.nzbs.find_one({'_id': nzb_id})
        nzb['articles'].sort(key=lambda x: int(x['part']))
        nzbfile = download_articles(news, nzb['articles'])
        #for a in nzb['articles']:
        #    response, number, msgid, lines = news.body(a['msgid'])
        #    if not response.startswith('222 '): raise Exception("Error downloading: '%s'" % response)
        #    #print (response[:10], number, msgid[:10], lines[:10])
        #    if lines[0] == '': lines = lines[1:]
        #    info = yencdecode.decode_from_lines(lines)
        #    nzbfile += open(info['tmpfilename']).read()
        #    os.remove(info['tmpfilename'])
        filename = uuid.uuid4()
        if 'rlsname' in nzb: filename = nzb['rlsname'] + ".nzb.gz"
        nzb['file'] = filename
        
        folder = get_folder(nzb)
        
        f = gzip.open(os.path.join(folder, filename), 'wb')
        f.write(nzbfile)
        f.close()
        if 'date' in nzb:
            t = time.mktime(nzb['date'].timetuple())
            os.utime(os.path.join(folder, nzb['file']), (t, t))

        nzb['stage'] = 2
        nzb['stages']['downloaded'] = True
        #del nzb['articles']
        db.nzbs.save(nzb)
        logging.info("Downloaded %s" % nzb['rlsname'])
        print "Downloaded %s" % nzb['rlsname']
        #pynotify.Notification("Release", nzb['rlsname']).show()
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
            print e
            print i
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
    for nzb in db.nzbs.find({'$or': [{'stage': 1, 'tags': "#a.b.teevee@EFNet"},
                                     {'stage': 1, 'tags': "#a.b.moovee@EFNet"}]}):
        if int(nzb['total']) == 1 and len(nzb['articles']) > 1:
            nzb['articles'] = nzb['articles'][:1]
            db.nzbs.save(nzb)
    
        if len(nzb['articles']) == int(nzb['total']):
            p.apply_async(download_nzb, [nzb['_id']])
    p.close()
    p.join()
    
    
