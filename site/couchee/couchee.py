#!/usr/bin/env python

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
from django.utils import simplejson

import util
from models import Movie, Cover
from upload import Upload, UploadCover, ServeHandler
import api
import re
from decorators import validate
import logging as l


def get_movies(order, direction, minvotes, maxvotes, minrating, maxrating, total_count=20, cursor=None):
    key = "[movies]%s;%s;%s;%s;%s;%s;%s;%s" % (order, direction, minvotes, maxvotes, minrating, maxrating, total_count, cursor)
    movies = memcache.get(key, namespace="movies")
    #if movies:
    #    l.info('Memcache hit in movies')
    #    return movies


    q = Movie.all()

    l.info((order, direction, minvotes, maxvotes, minrating, maxrating))
    maxrating = int(maxrating*10)
    minrating = int(minrating*10)
    if maxvotes > 200000: maxvotes = ()

    prefix = ''
    if direction == 'descending': prefix = '-'

    #if minvotes > 0: q = q.filter('imdbvotes >=', minvotes)
    #if maxvotes < 300000: q = q.filter('imdbvotes <=', maxvotes)

    #if minrating > 0: q = q.filter('imdbrating >=', minrating)
    #if maxrating < 100: q = q.filter('imdbrating <=', minrating)

    if order == 'age': q = q.order(prefix+'nzbdate')
    if order == 'name': q = q.order(prefix+'rlsname')
    if order == 'imdbrating': q = q.order(prefix+'imdbrating')
    if order == 'imdbvotes': q = q.order(prefix+'imdbvotes')

    if cursor: q = q.with_cursor(cursor)

    #tm = {}
    tm = []
    i = []
    count = 0
    date = None
    for m in q:
        if count == 20: break
        if not m.imdbrating: m.imdbrating = 0
        if not m.imdbvotes: m.imdbvotes = 0

        #How nice, a table scan :(
        if not (minrating <= m.imdbrating <= maxrating and minvotes <= m.imdbvotes <= maxvotes):
          continue
        else:
          count += 1

        if m.imdbid == None:
           m.imdbid = re.search('tt\d{7}', m.imdblink).group(0)
           #m.put()

        template_movie = {'type': 'movie'}
        #template_movie['counter'] = count
        template_movie['nzblink'] = m.nzblink
        template_movie['rlsname'] = m.rlsname
        template_movie['prettydate'] = util.pretty_date(m.nzbdate)
        template_movie['imdblink'] = m.imdblink
        template_movie['rtlink'] = 'http://www.rottentomatoes.com/alias?type=imdbid&s=%s' % m.imdbid[2:]

        if m.imdbinfo:
            template_movie['imdbinfo?'] = True
            template_movie['rating'] = m.imdbinfo.rating / 10.0
            template_movie['votes'] = m.imdbinfo.votes
            template_movie['imdbinfo'] = m.imdbinfo
            if m.imdbinfo.covers.count(1):
              template_movie['cover'] = '/serve/%s' % m.imdbinfo.covers[0].blobkey.key()
              i.append(template_movie)
        else:
            template_movie['imdbinfo?'] = False

        if not date == m.nzbdate.date():
            date = m.nzbdate.date()
            tm.append({'d': date, 'day': date.strftime('%A, %d %B %Y'), 'type': 'date'})
        #if not date in tm: tm[date] = {'d': date, 'day': date.strftime('%A, %d %B %Y'), 'movies': []}
        tm.append(template_movie)
        if count >= total_count: break

    movies = (tm, i, q.cursor())
    memcache.set(key, movies, namespace='movies')
    return movies

class AllItems(webapp.RequestHandler):
  def get(self):
    def jsonize(l, m):
      if 'rlsname' in m:
          return l + [m['rlsname']]
      else:
          return l

    movies = get_movies('name', 'ascending', 0, (), 0, 10, total_count=())
    self.response.out.write(simplejson.dumps(reduce(jsonize, movies[0], [])))

class ListMovies(webapp.RequestHandler):

  @validate('filter')
  def get(self, order, direction, minvotes, maxvotes, minrating, maxrating, cursor=None):
    movies = get_movies(order, direction, minvotes, maxvotes, minrating, maxrating, cursor=cursor)
    tm = movies[0]

    cursor = movies[2]

    if memcache.get(str(cursor)):
      cursor_uuid = memcache.get(str(cursor))
    else:
      cursor_uuid = uuid4()
      memcache.set('cursors.' + cursor_uuid.hex, cursor)
      memcache.set(str(movies[2]), cursor_uuid)

    template_values = {}
    template_values['items'] = tm
    template_values['filter'] = {'order': order, 'direction': direction, 'minvotes': minvotes, 'maxvotes': maxvotes, 'minrating': minrating, 'maxrating': maxrating}
    template_values['more_items'] = {'link': '?order=%s&direction=%s&minvotes=%s&maxvotes=%s&minrating=%s&maxrating=%s&cursor=%s' % (order, direction, minvotes, maxvotes, minrating, maxrating, cursor_uuid.hex)}
    #l.info(template_values)
    self.response.out.write(template.render('list_movies.html', template_values))

    #for cover in template_values['covers']:
    #  cover['link'] = '/serve/%s' % cover['imdbinfo'].covers[0].blobkey.key()
    #print '/moreitems/?uuid=' + str(cursor_uuid)


application = webapp.WSGIApplication([
  ('/', ListMovies),
  ('/allitems.json', AllItems),
  ('/upload', Upload),
  ('/upload_cover', UploadCover),
  ('/api/imdbinfo/(tt\d{7})/', api.ImdbInfo),
  ('/api/nzblink/(tt\d{7})/', api.NzbLink),
  ('/api/dummy/', api.Dummy),
  ('/serve/([^/]+)?', ServeHandler),
], debug=False)


def main():
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()

