#!/usr/bin/python

import urllib

class TMDB(object):

    def __init__(self, api_key, view='xml', lang='en'):
        ''' TMDB Client '''
        #view = yaml json xml
        self.lang = lang
        self.view = view
        self.key = api_key
        self.server = 'http://api.themoviedb.org'

    def socket(self, url):
        ''' Return URL Content '''

        data = None
        try:
            client = urllib.urlopen(url)
            data = client.read()
            client.close()
        except: pass
        return data

    def method(self, look, term):
        ''' Methods => search, imdbLookup, getInfo, getImages'''

        do = 'Movie.'+look
        term = str(term) # int conversion
        run = self.server+'/2.1/'+do+'/'+self.lang+'/'+self.view+'/'+self.key+'/'+term
        return run

    def method_people(self, look, term):
        ''' Methods => search, getInfo '''

        do = 'Person.'+look
        term = str(term) # int conversion
        run = self.server+'/2.1/'+do+'/'+self.lang+'/'+self.view+'/'+self.key+'/'+term
        return run

    def personResults(self, term):
        ''' Person Search Wrapper '''
        return self.socket(self.method_people('search',term))

    def person_getInfo(self, personId):
        ''' Person GetInfo Wrapper '''
        return self.socket(self.method_people('getInfo',personId))

    def searchResults(self, term):
        ''' Search Wrapper '''
        return self.socket(self.method('search',term))

    def getInfo(self, tmdb_Id):
        ''' GetInfo Wrapper '''
        return self.socket(self.method('getInfo',tmdb_Id))

    def imdbResults(self, titleTTid):
        ''' IMDB Search Wrapper '''
        return self.socket(self.method('imdbLookup',titleTTid))

    def imdbImages(self, titleTTid):
        ''' IMDB Search Wrapper '''
        titleTTid = 'tt0'+str(titleTTid)
        return self.socket(self.method('getImages',titleTTid))
