from google.appengine.ext import db
from google.appengine.ext import blobstore

class ImdbInfo(db.Model):
  name = db.StringProperty()
  year = db.IntegerProperty()
  votes = db.IntegerProperty()
  rating = db.RatingProperty()
  runtime = db.IntegerProperty()
  certification = db.StringProperty()
  short_plot = db.TextProperty()
  link = db.StringProperty()
  genre = db.StringListProperty()

class Cover(db.Model):
  imdbid = db.StringProperty()
  blobkey = blobstore.BlobReferenceProperty()
  imdbinfo = db.ReferenceProperty(ImdbInfo, collection_name='covers', required=True)
  
class Person(db.Model):  
  name = db.StringProperty()
  link = db.StringProperty()

class Cast(Person):
  movie = db.ReferenceProperty(ImdbInfo, collection_name='cast')
    
class Director(Person):
  movie = db.ReferenceProperty(ImdbInfo, collection_name='director')

class Movie(db.Model):
  rlsname = db.StringProperty()
  imdblink = db.StringProperty()
  nzblink = db.StringProperty()
  nzbdate = db.DateTimeProperty()
  image = db.StringProperty()
  imdbinfo = db.ReferenceProperty(ImdbInfo, collection_name='releases')
  imdbid = db.StringProperty()
