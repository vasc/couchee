import re
import pymongo
from nntplib import NNTP
from lxml import objectify
from lxml.etree import XMLSyntaxError
from nntplib import NNTPTemporaryError
import gzip
import os
from download import download_articles
import logging
from themoviedb.tmdb import TMDB
import json
import urllib
from PIL import Image
import urllib2
import sys
import util
import xmlquery
import html2xml


def tv_meta_info(rlsname):
    m = re.match('(.*)(-.*)$', rlsname)
    if m: rlsname = re.sub('-', '.', m.group(1)) + m.group(2)
    rlsname = re.sub('_', '.', rlsname)

    #regular
    m1 = re.search(r'^(?P<show>(\w+\.)+?)s(?P<s>\d?\d)\.?e(?P<e>\d\d)(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #regular with x
    m2 = re.search(r'^(?P<show>(\w+\.)+?)(?P<s>\d?\d)x(?P<e>\d\d)(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #by day
    m3 = re.search(r'^(?P<show>\w+\.)+?(\d\d)?\d\d\.\d\d\.\d\d(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #fov style
    m4 = re.search(r'^(?P<show>(\w+_)*\w+)\.(?P<s>\d?\d)x(?P<e>\d\d)\.(\w+_)*\w+(\.\w+)*-(\w+\.)*\w+$', rlsname, re.I)
    #multiple episode
    m5 = re.search(r'^(?P<show>\w+\.)+?s\d\de\d\d-?e?\d\d(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #disc style
    m6 = re.search(r'^(?P<show>\w+\.)+?s\d\dd\d?\d(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    #full season
    m7 = re.search(r'^(?P<show>\w+\.)+?s\d\d(\.\w+)+-(\w+\.)*\w+$', rlsname, re.I)
    m = None
    #if m4: m = m4
    if m2: m = m2
    if m1: m = m1

    if m:
        #print "%s S%sE%s" % (re.sub('[\._]', ' ', m.group('show')), m.group('s'), m.group('e'))
        pass
    else: pass#print rlsname
    return m1 or m2 or m3 or m5 or m6 or m7

def meta_nzbs():
    from pprint import pprint
    db = pymongo.Connection().usenet
    count = {}
    count[True] = 0
    count[False] = 0
    no_id = []
    shows = {}
    for nzb in db.nzbs.find({'stage': 2, 'tags': '#a.b.teevee@EFNet'}):
        rlsname = nzb['rlsname'].lower()
        rlsname = re.sub('_', '.', rlsname)

        r = tv_meta_info(nzb['rlsname'])
        count[bool(r)] += 1
        if r:
            s = r.group('show').lower()
            if not s in shows: shows[s] = 1
            else: shows[s] += 1
        else: no_id.append(nzb['rlsname'].lower())
    no_id.sort()

    #pprint(sorted(shows, key=lambda s: shows[s]))

    pprint(shows)
    print count


def download_posters():
    db = pymongo.Connection().usenet
    dbmovies = pymongo.Connection().imdb
    folder = db.config.find_one({'type': 'folder', 'category': 'meta'})['folders']['movies']

    tmdb = TMDB('f765d363ee59032855f018253ae2a266', 'json', 'en')
    for nzb in db.nzbs.find({'stages.movieid': True, 'stages.poster': {'$ne': True}}):
        m = dbmovies.movies.find_one({'_id': nzb['movieid']})
        if m and 'poster' in m['stages']:
            nzb['stages']['poster'] = True
            db.nzbs.save(nzb)
            continue

        if not m: m = {'_id': nzb['movieid'], 'stages': [], 'posters': []}
        if not 'posters' in m: m['posters'] = []

        imdb_info = tmdb.imdbResults(nzb['movieid'])
        obj = json.loads(imdb_info)[0]
        count = 1

        if 'posters' in obj:
            for p in obj['posters']:
                p = p['image']
                if p['type'] == 'poster' and p['size'] == 'original':
                    v = 'y'
                    print v, nzb['rlsname'], p['url']
                    f = nzb['movieid']+'.'+str(count)+'.jpg'
                    if download_poster(p['url'], os.path.join(folder, f)):
                        m['posters'].append(f)
                        count += 1
                        logging.info("Poster %s %s" % (nzb['rlsname'], f))
                        print "Poster %s %s" % (nzb['rlsname'], f)
                    else: "Error downloading %s" % p['url']

        dbmovies.movies.save(m)
        nzb['stages']['poster'] = True
        db.nzbs.save(nzb)

@util.retry(IOError, 3, 2, silent_fail=True)
def download_poster(url, f):
    urllib.urlretrieve(url, f)
    im = Image.open(f)
    return True


def get_imdb_info():
    db = pymongo.Connection().usenet
    dbmovies = pymongo.Connection().imdb
    mem = util.Memcached()

    for nzb in db.nzbs.find({'stages.movieid': True, 'stages.imdb_info': {'$ne': True}, 'stages.direct_imdb': {'$ne': True}}):
        m = dbmovies.movies.find_one({'_id': nzb['movieid']})
        if not m: m = {'_id': nzb['movieid'], 'stages': []}
        if not ('name' in m['stages'] and 'votes' in m['stages'] and 'rating' in m['stages'] and 'year' in m['stages'] and 'short_plot' in m['stages']):
            info = imdb_direct_info(nzb['movieid'])
            #if imdb_info(nzb['movieid'], m, mem):
            #    nzb['stages']['imdb_info'] = True
            #    db.nzbs.save(nzb)
            #else:
            #    nzb['stages']['direct_imdb'] = True
            #    db.nzbs.save(nzb)
            #    print '\rMovie [http://www.imdb.com/title/%s] is not featured' % nzb['movieid']


def imdb_direct_info(imdb_id):
    print imdb_id

    try:
        html = urllib2.urlopen('http://www.imdb.com/title/'+imdb_id+'/').read()
    except urllib2.HTTPError as e:
        print e
        return

    html = re.sub(r'&#x(\w+);', r'%\1', html)

    try:
        html = unicode(html, 'utf-8')
    except UnicodeDecodeError as e:
        print "UnicodeDecodeError (%s) in %s" % (e, m)
        return

    html = urllib2.unquote(html)
    xml = html2xml.translate(html)
    page = xmlquery.parse_xml(xml)

    info = page.queryone('#overview-top')
    if not info: return

    name = str(info.queryone('h1.header').children[0])
    print name

    year = info.queryone('h1.header>span>a')
    if year: year = int(year.text)
    print year

    genres = map(lambda x: x.text, info.query('.infobar>a[href^="/genre/"]'))
    print genres

    rating = str(info.queryone('span[class="rating-rating"]').children[0])
    if rating == '-': rating = 0
    else: rating = float(rating)
    print rating

    votes = int(re.sub(',', '', info.queryone('a[href="ratings"]').text.split()[0]))
    print votes

    if len(info.query('p')) > 1:
        short_plot = info.query('p')[1].text.splitlines()[0]
    else:
        short_plot = None
    print short_plot

    people = {}
    for p_type in info.query('div.txt-block'):
        p_type_text = p_type.queryone('h4.inline').text[:-1]
        people[p_type_text] = []
        for p in p_type.query('a[href^="/name/"]'):
            people[p_type_text].append((p.text, p.attributes['href']))
    print people
    return

    raise NotImplementedError()

    (name, year) = re.search('<meta name="title" content="(.*?)\s\((\d{4})(?:/[IVX]+)?\)(?:\s\(T?V\))?">', html).group(1, 2)
    m = re.search('<a href="ratings" class="tn15more">(\d+(?:,\d+)?) votes</a>', html)

    if m: mvotes = int(re.sub(',', '', m.group(1)))
    else: mvotes = 0

    print name, year, mvotes

@util.retry(pymongo.errors.OperationFailure, 10, 3)
def imdb_info(imdb_id, movie, mem = None):
    start = 1
    db = pymongo.Connection().imdb

    html = urllib2.urlopen('http://www.imdb.com/title/'+imdb_id+'/').read()
    print 'Identifying http://www.imdb.com/title/%s/' % imdb_id,
    sys.stdout.flush()
    (name, year) = re.search('<meta name="title" content="(.*?)\s\((\d{4})(?:/[IVX]+)?\)(?:\s\(T?V\))?">', html).group(1, 2)
    m = re.search('<a href="ratings" class="tn15more">(\d+(?:,\d+)?) votes</a>', html)

    if m: mvotes = int(re.sub(',', '', m.group(1)))
    else: mvotes = 0


    url = 'http://www.imdb.com/search/title?sort=num_votes,desc&title_type=feature&year=%s,%s&start=' % (year, year)
    html = urllib2.urlopen(url).read()
    #html = re.sub(r'&#x(\w+);', r'%\1', m)


    total = re.search(r'(\d+(?:,\d+)?)\ntitles', html)
    total = int(re.sub(',', '', total.group(1)))

    last_page = total/50 + 1
    pages = set(range(0, last_page))

    mm = last_page
    mi = 1

    while len(pages) > 0:
        ep = (mm+mi)/2
        page = reduce(lambda x,y: x if abs(ep-x) < abs(ep-y) else y ,pages)
        pages.remove(page)

        if page > mm or page < mi: return False

        start = page * 50 + 1

        print "\rIdentifying %s: page %s  " % (name, page),
        sys.stdout.flush()

        if mem and mem.testkey(url+str(start)):
            html = mem.getkey(url+str(start))
            print 'in memcached :)',
        else:
            print 'not in memchached :(',
            f = urllib2.urlopen(url+str(start))
            html = f.read()
            html = re.sub(r"\&nbsp;", "", html)
            html = re.sub(re.compile(r'<script.*?</script>', re.S), "", html)
            if mem: mem.setkey(url+str(start), html)

        ms = re.findall(r'<tr class="(?:(?:even)|(?:odd)) detailed">(.*?)</tr>', html, re.S)
        for m in ms:
            #movie = {}
            #movie['stages'] = []
            m = re.sub(r'&#x(\w+);', r'%\1', m)

            try:
                m = unicode(m, 'utf-8')
            except UnicodeDecodeError as e:
                #print "UnicodeDecodeError (%s) in %s" % (e, m)
                continue

            m = urllib2.unquote(m)

            votes = re.sub(',', '', re.search(r'<td class="sort_col">(.*?)</td>', m).group(1))

            (movie['link'], movie['name'], movie['year']) = re.search(r'<a href="(/title/tt\d{7,}/)">(.*?)</a>[\s\n]*<span class="year_type">\((.*?)\)</span>', m).group(1, 2, 3)
            if not movie['link'] == '/title/'+imdb_id+'/': continue

            if votes == '-': movie['votes'] = 0
            else: movie['votes'] = int(votes)
            votes = movie['votes']


            rating = re.search(r'<span class="rating-rating">(.*?)<span>', m).group(1)
            if rating == '-': movie['rating'] = 0
            else: movie['rating'] = float(rating)

            shortplot = re.search(r'<span class="outline">(.*?)</span>', m, flags=re.S)
            if shortplot: movie['short_plot'] = unicode(shortplot.group(1))

            director = []
            if re.search(r'Dir:', m):
                for n in re.findall(r'<a href="/name/nm\d+?/">.+?</a>', re.search(r'Dir:.*$', m, flags=re.M).group(0)):
                    director.append(re.search(r'<a href="(/name/nm\d+?/)">(.+?)</a>', n).groups())
            if director: movie['director'] = director
            movie['stages'].append('director')

            cast = []
            if re.search(r'With:', m):
                for n in re.findall(r'<a href="/name/nm\d+?/">.+?</a>', re.search(r'With:.*$', m, flags=re.M).group(0)):
                    cast.append(re.search(r'<a href="(/name/nm\d+?/)">(.+?)</a>', n).groups())
            if cast: movie['cast'] = cast
            movie['stages'].append('cast')

            genre = []
            if re.search(r'<span class="genre">.*?</span>', m, flags=re.S):
                for n in re.findall(r'<a href="/genre/\w+">\w+</a>', re.search(r'<span class="genre">.*?</span>', m, flags=re.S).group(0)):
                    genre.append(re.search(r'<a href="/genre/\w+">(\w+)</a>', n).group(1))
            if genre: movie['genre'] = genre
            movie['stages'].append('genre')

            cert = re.search(r'<span class="certificate"><img width="\d+" alt="(\w+?)"', m)
            if cert: movie['certification'] = cert.group(1)

            runtime = re.search(r'span class="runtime">(\d+) mins.</span>', m)
            if runtime: movie['runtime'] = int(runtime.group(1))

            movie['stages'].extend(['name', 'year', 'votes', 'certification', 'rating', 'runtime', 'short_plot'])
            movie['_id'] = re.search(r'tt\d{7,}', movie['link']).group(0)

            print "\rIdentified %s as %s (%s) %s / %s" % (movie['_id'], movie['name'], movie['year'], movie['rating'], movie['votes'])
            db.movies.save(movie)
            return True
        if mi == mm: return False
        #print mi, page, mm, '=>',
        if votes > mvotes: mi = page
        else: mm = page
        #print mi, mm

    return False










def id_movies():
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'stage': 2, 'tags': '#a.b.moovee@EFNet'}):
        if 'error' in nzb['stages']: continue #
        #if 'no imdb' in nzb['stages']: continue #print 'No IMDB', nzb['rlsname'];
        #if 'no nfo' in nzb['stages']: continue #print 'No IMDB', nzb['rlsname'];
        folder = db.config.find_one({'type': 'folder', 'category': 'moovee'})['folder']
        filename = nzb['file']
        nntp = NNTP('eu.news.astraweb.com', user='vasc', password='dZeZlO89hY6F')
        try:
            it = False
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
                            nzb['stages']['movieid'] = True
                            db.nzbs.save(nzb)

                            print 'ID', nzb['rlsname'], 'as http://www.imdb.com/title/tt' + m.group(1) + '/'
                            logging.info('ID ' + nzb['rlsname'] + ' as http://www.imdb.com/title/tt' + m.group(1) + '/')
                        else:
                            print 'Unable to identify', nzb['rlsname']
                            nzb['error'] = {'value': 422, 'msg': '', 'help': 'nfo does not contain identifiable imdb link'}
                            nzb['stages']['error'] = 'no imdb'
                            db.nzbs.save(nzb)
                        it = True
                        break
                        #else: print nzb['file']
            if not it:
                print 'No nfo in nzb', nzb['rlsname']
                nzb['error'] = {'value': 423, 'msg': '', 'help': 'nzb file does not contain nfo'}
                nzb['stages']['error'] = 'no nfo'
                db.nzbs.save(nzb)
        except XMLSyntaxError as e:
            nzb['error'] = {'value': 420, 'msg': str(e), 'help': 'nzb file is not valid xml'}
            nzb['stage'] = 400
            nzb['stages']['error'] = True
            db.nzbs.save(nzb)
        except NNTPTemporaryError as e:
            if str(e).startswith('430'):
                nzb['error'] = {'value': 421, 'msg': str(e), 'help': 'nfo article is not available in server, waiting for a backup server'}
                nzb['stages']['error'] = '430 nfo'
                db.nzbs.save(nzb)
            print articles, e
        #except Exception:
        #     print 'error'
        #     continue
        #break

