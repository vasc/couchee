#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
from datetime import datetime
import wsgiref.handlers
from uuid import uuid4
import random as r
import pickle

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

import util
from models import Movie, Cover
from upload import Upload, UploadCover, ServeHandler
import api
import re


def get_movies(cursor=None):
    q = Movie.all().order('-nzbdate')
    if cursor: q = q.with_cursor(cursor)
    
    tm = {}
    for m in q.fetch(50):
        if m.imdbid == None:
            m.imdbid = re.search('tt\d{7}', m.imdblink).group(0)
            #m.put()
    
        template_movie = {}
        #template_movie['counter'] = count
        template_movie['nzblink'] = m.nzblink
        template_movie['rlsname'] = m.rlsname
        template_movie['prettydate'] = util.pretty_date(m.nzbdate)
        template_movie['imdblink'] = m.imdblink
        template_movie['rtlink'] = 'http://www.rottentomatoes.com/alias?type=imdbid&s=%s' % m.imdbid[2:]
        
        if m.imdbinfo:
            template_movie['imdbinfo'] = True
            template_movie['rating'] = m.imdbinfo.rating / 10.0
            template_movie['votes'] = m.imdbinfo.votes
        else:
            template_movie['imdbinfo'] = True
        #count += 1
        
        date = m.nzbdate.date()
        if not date in tm: tm[date] = {'d': date, 'day': date.strftime('%A, %d %B %Y'), 'movies': []}
        tm[date]['movies'].append(template_movie)
    return (tm, q.cursor())

class MoreItems(webapp.RequestHandler):
  def get(self):
    req = self.request.get('uuid')
    if not req: return
    cursor = memcache.get(req)
    if not cursor: return
    movies = get_movies(cursor)
    self.response.out.write(template.render('items.html', {'days': sorted(movies[0].values(), reverse=True)}))

class MainPage(webapp.RequestHandler):
  def get(self, order="newer", page=1):
    if not order in ['newer', 'older', 'popular', 'rating']:
        self.response.set_status(404)
        return
    movies = get_movies()
    tm = movies[0]
    cursor_uuid = uuid4()
    memcache.set(str(cursor_uuid), movies[1])
    template_values = {}
    template_values['days'] = sorted(tm.values(), reverse=True)
    template_values['covers'] = []
    for cover in Cover.all():
      template_values['covers'].append({'link': '/serve/%s' % cover.blobkey.key(), 'name': cover.imdbinfo.name}) 
    
    self.response.out.write(template.render('index.html', template_values))
    #print '/moreitems/?uuid=' + str(cursor_uuid)
    
class DisplayCovers(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""<!DOCTYPE html>
<html lang="en">
  <head>
  </head>
  <body>""")
    for cover in Cover.all().fetch(22):
      img = '    <img src="/serve/%s" height="240px" width="160px" />' % cover.blobkey.key() 
      self.response.out.write(img)
    self.response.out.write("""  </body>
</html>""")
        
application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/moreitems/', MoreItems),
  ('/covers/', DisplayCovers),
  ('/upload', Upload),
  ('/upload_cover', UploadCover),
  ('/api/missing/([^/]+)/([^/]+)/', api.Missing),
  ('/api/imdbinfo/(tt\d{7})/', api.ImdbInfo),
  ('/serve/([^/]+)?', ServeHandler),
], debug=True)


def main():
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
