import models
import logging
import hashlib

from google.appengine.ext import webapp
from django.utils import simplejson


api_key = 'e8aAqE7pFcKjuTnAoTe4'

def test_key(handler):
    return handler.request.get('apikey') == api_key

class Dummy(webapp.RequestHandler):
    def get(self):
        self.response.out.write('dummy')
        return

class NzbLink(webapp.RequestHandler):
    def get(self, imdbid):
        nzbs = models.Movie.all().filter("imdblink =", "http://www.imdb.com/title/" + imdbid + "/");

        results = []
        for m in nzbs:
            r = {"rlsname": m.rlsname,
                 "nzblink": m.nzblink,
                 "imdbid": imdbid
            }
            results.append(r);

        self.response.out.write(simplejson.dumps(results))


class ImdbInfo(webapp.RequestHandler):
    def get(self, imdbid):
        m = models.ImdbInfo.get_by_key_name(imdbid)
        if not m:
            self.response.set_status(404)
            return

        r = {'name': m.name,
             'year': m.year,
             'votes': m.votes,
             'rating': m.rating / 100.0,
             'runtime': m.runtime,
             'certification': m.certification,
             'short_plot': m.short_plot,
             'link': m.link,
             '_id': m.key().name()}

        r['genre'] = [g for g in m.genre]
        r['cast'] = [{'name': actor.name, 'imdb_link': actor.link} for actor in m.cast]
        r['director'] = [{'name': director.name, 'imdb_link': director.link} for director in m.director]

        self.response.out.write(simplejson.dumps(r))

    def post(self, imdbid):
        if not test_key(self):
            self.response.set_status(403)
            return

        logging.debug('Creating info for %s' % imdbid)
        m = models.ImdbInfo.get_by_key_name(imdbid)
        if not m: m = models.ImdbInfo(key_name=imdbid)

        r = simplejson.loads(self.request.get('movie'))

        m.name = r['name']
        m.year = int(r['year'])
        m.votes = r['votes']
        m.rating = int(r['rating'] * 10)
        if 'runtime' in r: m.runtime = r['runtime']

        if 'certification' in r: m.certification = r['certification']
        if 'short_plot' in r: m.short_plot = r['short_plot']
        m.link = r['link']
        if 'genre' in r: m.genre = r['genre']
        else: m.genre = []
        m.put()

        if 'cast' in r:
            for actor in r['cast']:
                key = imdbid+':'+actor[0]
                models.Cast.get_or_insert(key, **{'name': actor[1], 'link': actor[0], 'movie': m})

        if 'director' in r:
            for director in r['director']:
                key = imdbid+':'+director[0]
                models.Cast.get_or_insert(key, **{'name': director[1], 'link': director[0], 'movie': m})

        logging.debug(m.link)
        for rls in models.Movie.all().filter('imdblink =', 'http://www.imdb.com'+m.link):
            logging.debug(rls)
            if rls.imdbinfo == None:
                logging.debug('%s linked to %s (%s)' % (rls.rlsname, m.name, m.key().name()))
                rls.imdbinfo = m
                rls.imdbrating = m.rating
                rls.imdbvotes = m.votes
                rls.put()

        logging.info('Movie with id %s saved' % imdbid)
        self.redirect('/api/imdbinfo/%s/' % imdbid)


class Missing(webapp.RequestHandler):
    def get(self, model_name, parameter_name):
        if not self.test_sane(model_name, parameter_name): return

        model = getattr(models, model_name)

        c = 0
        for m in model.all():
            if c == 100: return
            if getattr(m, parameter_name) == None:
                self.response.out.write(m.key().name())
                c += 1

    def post():
        if not self.test_sane(model_name, parameter_name): return

        model = getattr(models, model_name)
        m = model.get_by_key_name(self.get('key'))
        setattr(m, parameter_name, self.get('value'))

        self.redirect('/')

    def test_sane(self, model_name, parameter_name):
        if not test_key(self):
            self.response.set_status(403)
            logging.warning('API: denied access to %s with apikey: "%s"' % (self.request.path, self.request.get('apikey')))
            return

        if not model_name in dir(models):
            self.response.set_status(404)
            logging.info('API: model "%s" not found' % model_name)
            return

        model = getattr(models, model_name)

        if not parameter_name in dir(model):
            self.response.set_status(404)
            logging.info('API: parameter "%s" not found in model "%s"' % (model_name, parameter_name))
            return

