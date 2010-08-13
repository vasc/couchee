import urllib2
import re
from themoviedb.tmdb import TMDB
from pprint import pprint
import pymongo


def download_info(year_start, year_end = None):
    if not year_end or year_end < year_start: year_end = year_start
    url = 'http://www.imdb.com/search/title?sort=num_votes,desc&title_type=feature&year=%s,%s&start=' % (year_start, year_end)
    start = 1
    
    votes = 1000
    rating = []
    db = pymongo.Connection().imdb
    
    
    while votes >= 1000:
        f = urllib2.urlopen(url+str(start))
        print url+str(start)
        html = f.read()
        html = re.sub(r"\&nbsp;", "", html)
        html = re.sub(re.compile(r'<script.*?</script>', re.S), "", html)
        #html = re.sub("\n", "", html)
        #print html
        
        ms = re.findall(r'<tr class="(?:(?:even)|(?:odd)) detailed">(.*?)</tr>', html, re.S)
        for m in ms:
            movie = {}
            movie['stages'] = []
            m = re.sub(r'&#x(\w+);', r'%\1', m)
            
            try:
                m = unicode(m, 'utf-8')
            except UnicodeDecodeError as e:
                print "UnicodeDecodeError (%s) in %s" % (e, m)
                continue 
                
            m = urllib2.unquote(m)
            
            movie['votes'] = int(re.sub(',', '', re.search(r'<td class="sort_col">(.*?)</td>', m).group(1)))
            votes = movie['votes']
            
            movie['rating'] = float(re.search(r'<span class="rating-rating">(.*?)<span>', m).group(1))
            
            (movie['link'], movie['name'], movie['year']) = re.search(r'<a href="(/title/tt\d{7,}/)">(.*?)</a>[\s\n]*<span class="year_type">\((.*?)\)</span>', m).group(1, 2, 3)
            
            shortplot = re.search(r'<span class="outline">(.*?)</span>', m, flags=re.S)
            if shortplot: movie['short_plot'] = unicode(shortplot.group(1))
            
            #movie['director'] = re.search(r'Dir: (?:<a href="(/name/nm\d+?/)">(.+?)</a>(?:, )?)+', m)
            
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
            
            print "%s %s (%s) %s" % (movie['votes'], movie['name'], movie['_id'], movie['rating'])
            db.movies.save(movie)
            
            #IMDB_TTID = re.search(r'(tt\d{7,})', m).group(1)
            #print IMDB_TTID
            #tmdb = TMDB('f765d363ee59032855f018253ae2a266', 'json', 'en')
            #imdb_images = tmdb.imdbResults(IMDB_TTID)
            #print imdb_images
        start += 50
        print start

    
    from pylab import scatter, show
    scatter(rating, votes, c='b', marker='o')
    show()




if __name__ == "__main__":
    download_info(1800, 1899)

