import pymongo
from themoviedb.tmdb import TMDB
import json
import pprint
import urllib

db = pymongo.Connection().usenet
#for movie in db.movies.find({"votes": {'$lt': 5000}}).sort('votes', pymongo.DESCENDING).limit(100).skip(0):
for movie in db.nzbs.find({"stages.movieid": True}):#.sort('votes', pymongo.DESCENDING).limit(100).skip(0):
    tmdb = TMDB('f765d363ee59032855f018253ae2a266', 'json', 'en')
    imdb_info = tmdb.imdbResults(movie['movieid'])
    obj = json.loads(imdb_info)[0]
    
    v = 'n'
    url = ''
    count = 1
    
    if 'posters' in obj:
          for p in obj['posters']:
              p = p['image']
              if p['type'] == 'poster' and p['size'] == 'cover':
                  v = 'y',
                  url = p['url']
                  urllib.urlretrieve(url, 'poster/'+movie['movieid']+'.'+str(count)+'.jpg')
                  count += 1
                  print v, movie['rlsname'], url
