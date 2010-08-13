import pymongo
from themoviedb.tmdb import TMDB
import json
import pprint

db = pymongo.Connection().imdb
for movie in db.movies.find({"votes": {'$lt': 5000}}).sort('votes', pymongo.DESCENDING).limit(100).skip(0):
    tmdb = TMDB('f765d363ee59032855f018253ae2a266', 'json', 'en')
    imdb_info = tmdb.imdbResults(movie['_id'])
    obj = json.loads(imdb_info)[0]
    
    v = 'n'
    url = ''
    
    if 'posters' in obj:
          for p in obj['posters']:
              p = p['image']
              if p['type'] == 'poster' and p['size'] == 'cover':
                  v = 'y',
                  url = p['url']
                  break
    print v, movie['name'], url
