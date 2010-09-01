import boto
import pymongo
from boto.s3.connection import S3Connection
from uuid import uuid4
from download import get_folder
import os
from boto.s3.key import Key
import sys
import urllib
import urllib2
import logging
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import hashlib
import simplejson
import tempfile
from PIL import Image


def upload_nzbs():
    conn = S3Connection('AKIAIOQYUVE7OETHE5XA', 'Ckqs+ThC5v29r7sXGj9qICfvX1UqF2n7hZcM/4Rr')
    bucket_name = 'couchee'
    bucket = conn.get_bucket(bucket_name)
    db = pymongo.Connection().usenet

    for nzb in db.nzbs.find({'stages.uploaded': {'$ne': True}, 'stages.downloaded': True, 'tags':'#a.b.moovee@EFNet'}):
        k = Key(bucket)
        k.key = 'moovee/' + nzb['file'][:-3]
        k.set_metadata('Content-Encoding', 'gzip')
        k.set_metadata('Content-Disposition', 'attachment; filename=%s' % nzb['file'][:-3])
        folder = get_folder(nzb)
        k.set_contents_from_filename(os.path.join(folder, nzb['file']))
        k.make_public()
        nzb['url'] = 'http://' + bucket_name + '.s3.amazonaws.com/' + k.key
        print nzb['url']
        nzb['stages']['uploaded'] = True
        logging.info("Uploaded %s to %s" % (nzb['rlsname'], nzb['url']))
        db.nzbs.save(nzb)
        k.close()
        #print nzb
        #break

def movie_publish():
    db = pymongo.Connection().usenet
    dbmovies = pymongo.Connection().imdb
    for nzb in db.nzbs.find({'tags':'#a.b.moovee@EFNet', 'stages.movie_publish': {'$ne': True}}):
        m = dbmovies.movies.find_one({'_id': nzb['movieid']})
        if not 'published_info' in m['stages']:
            data = urllib.urlencode([('apikey', 'e8aAqE7pFcKjuTnAoTe4'), ('movie', simplejson.dumps(m))])
            urllib2.urlopen('http://coucheeb.appspot.com/api/imdbinfo/%s/' % m['_id'], data)
            m['stages'].append('published_info')
            dbmovies.movies.save(m)
            print 'Published %s (%s)' % (m.name, m['_id'])
        nzb['stages']['movie_publish'] = True
        db.nzbs.save(nzb)    

def movie_local_publish():
    db = pymongo.Connection().usenet
    dbmovies = pymongo.Connection().imdb
    for nzb in db.nzbs.find({'stages.uploaded': True, 'stages.downloaded': True, 'stages.movieid': True, 'tags':'#a.b.moovee@EFNet'}).limit(320):
        movie = dbmovies.movies.find_one({'_id': nzb['movieid'], 'stages': 'name'})
        if movie:
            data = urllib.urlencode([('apikey', 'e8aAqE7pFcKjuTnAoTe4'), ('movie', simplejson.dumps(movie))])
            r = urllib2.urlopen('http://localhost:8080/api/imdbinfo/%s/' % movie['_id'], data)
            print 'Local published %s (%s)' % (movie['name'], movie['_id'])

def cover_publish():
    db = pymongo.Connection().usenet
    dbmovies = pymongo.Connection().imdb
    folder = db.config.find_one({'type': 'folder', 'category': 'meta'})['folders']['movies']
    register_openers()
    
    for nzb in db.nzbs.find({'stages.published': True, 'stages.poster': True, 'stages.movie_publish': True, 'tags':'#a.b.moovee@EFNet'}):
        data = urllib.urlencode([('secret', 'e8aAqE7pFcKjuTnAoTe4'), ('simple', 'true')])
        #
        m = dbmovies.movies.find_one({'_id': nzb['movieid']})
        if not m or not 'posters' in m:
            del nzb['stages']['poster']
            db.nzbs.save(nzb)
            continue
        if not 'cover_publish' in m['stages']:
            for p in m['posters']:
                im = Image.open(os.path.join(folder, p))
                im.resize((134, 193), Image.ANTIALIAS)
                f = tempfile.TemporaryFile()
                im.save(f, 'jpeg')
                f.seek(0)
                hexhash = hashlib.sha1(f.read()).hexdigest()
                f.seek(0)
                url = urllib2.urlopen('http://coucheeb.appspot.com/upload_cover?%s' % data).read()
                datagen, headers = multipart_encode({"cover": f, 'hexhash': hexhash, 'imdbid': nzb['movieid']})
                request = urllib2.Request(url, datagen, headers)
                urllib2.urlopen(request).read()
                print 'Uploaded cover for release: %s' % nzb['rlsname']
            m['stages'].append('cover_publish')    
        nzb['stages']['cover_publish'] = True

def cover_local_publish():
    db = pymongo.Connection().usenet
    dbmovies = pymongo.Connection().imdb
    folder = db.config.find_one({'type': 'folder', 'category': 'meta'})['folders']['movies']
    register_openers()
    
    for nzb in db.nzbs.find({'stages.published': True, 'stages.poster': True, 'tags':'#a.b.moovee@EFNet'}):
        data = urllib.urlencode([('secret', 'e8aAqE7pFcKjuTnAoTe4'), ('simple', 'true')])
        #
        m = dbmovies.movies.find_one({'_id': nzb['movieid']})
        if not m or not 'posters' in m:
            del nzb['stages']['poster']
            db.nzbs.save(nzb)
            continue
        for p in m['posters']:
            im = Image.open(os.path.join(folder, p))
            im = im.resize((134, 193), Image.ANTIALIAS)
            f = tempfile.TemporaryFile()
            im.save(f, 'jpeg')
            f.seek(0)
            hexhash = hashlib.sha1(f.read()).hexdigest()
            f.seek(0)
            url = urllib2.urlopen('http://localhost:8080/upload_cover?%s' % data).read()
            datagen, headers = multipart_encode({"cover": f, 'hexhash': hexhash, 'imdbid': nzb['movieid']})
            request = urllib2.Request(url, datagen, headers)
            urllib2.urlopen(request).read()
            print 'uploaded cover for release: %s' % nzb['rlsname']
            break
        

def local_publish():
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'stages.uploaded': True, 'stages.downloaded': True, 'stages.movieid': True, 'tags':'#a.b.moovee@EFNet'}).limit(320):
        data = urllib.urlencode([('rlsname', nzb['rlsname']), ('nzblink', nzb['url']), ('imdblink', nzb['link']), ('nzbdate', str(nzb['date'])), ('secret', 'e8aAqE7pFcKjuTnAoTe4')])
        r = urllib2.urlopen('http://localhost:8080/upload', data)
        print nzb['rlsname']

        
def publish_nzbs():
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'stages.published': {'$ne': True}, 'stages.uploaded': True, 'stages.downloaded': True, 'stages.movieid': True, 'tags':'#a.b.moovee@EFNet'}):
        data = urllib.urlencode([('rlsname', nzb['rlsname']), ('nzblink', nzb['url']), ('imdblink', nzb['link']), ('nzbdate', str(nzb['date'])), ('secret', 'e8aAqE7pFcKjuTnAoTe4')])
        r = urllib2.urlopen('http://coucheeb.appspot.com/upload', data)
        if r.geturl() == 'http://coucheeb.appspot.com/':
            nzb['stages']['published'] = True
            db.nzbs.save(nzb)
            print 'published', nzb['rlsname']
            logging.info("Published %s" % nzb['rlsname'])
        else:
            print 'error publishing',  nzb['rlsname']
        
