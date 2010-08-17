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

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

class Movie(db.Model):
  rlsname = db.StringProperty()
  imdblink = db.StringProperty()
  nzblink = db.StringProperty()
  nzbdate = db.DateTimeProperty()


class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Teevee</title>   
    <link rel="stylesheet" href="/media/main.css" type="text/css" />
  </head>
  <body id="index" class="home">
    <ul id="shows_list">\n""")

    movies = db.GqlQuery("SELECT * "
                         "FROM Movie "
                         "ORDER BY nzbdate DESC LIMIT 5000")

    count = 1
    for m in movies:
        self.response.out.write(6*' ' + '<li>\n')
        self.response.out.write(8*' ' + '%d. <a href="%s"><span class="rlsname">%s</span></a>\n' % (count, m.nzblink, m.rlsname))
        self.response.out.write(8*' ' + '<span class="age">%s</span> <a href="%s" class="imdb">[imdb]</a>\n' % (pretty_date(m.nzbdate), m.imdblink))
        self.response.out.write(6*' ' + '</li>\n')
        count += 1
        
    self.response.out.write(4*' ' + """</ul>
  </body>
</html>""")


class Upload(webapp.RequestHandler):
    def post(self):
        m = Movie()

        m.rlsname = self.request.get('rlsname')
        m.imdblink = self.request.get('imdblink')
        m.nzblink = self.request.get('nzblink')
        m.nzbdate = datetime.strptime(self.request.get('nzbdate'), "%Y-%m-%d %H:%M:%S")
        m.put()
        self.redirect('/')


def pretty_date(time):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    diff = now - time
    
    #if type(time) is int:
    #    diff = now - datetime.fromtimestamp(time)
    #elif not time:
    #    diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "yesterday"
    #if day_diff < 7:
    return str(day_diff) + " days ago"
    #if day_diff < 31:
    #    return str(day_diff/7) + " weeks ago"
    #if day_diff < 365:
    #    return str(day_diff/30) + " months ago"
    #return str(day_diff/365) + " years ago"


application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/upload', Upload)
], debug=True)


def main():
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
