from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import memcache


from datetime import datetime
import urllib
import logging
import re

from models import Movie, Cover, ImdbInfo

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class Upload(webapp.RequestHandler):
    def post(self):
        
        if self.request.get('secret') == 'e8aAqE7pFcKjuTnAoTe4':
            m = Movie(key_name=self.request.get('nzblink'))
            m.rlsname = self.request.get('rlsname')
            m.imdblink = self.request.get('imdblink')
            m.imdbid = re.search('tt\d{7}', m.imdblink).group(0)
            m.nzblink = self.request.get('nzblink')
            m.nzbdate = datetime.strptime(self.request.get('nzbdate'), "%Y-%m-%d %H:%M:%S")
            
            info = ImdbInfo.get_by_key_name(m.imdbid)
            if info: m.imdbinfo = info
            m.put()
            self.redirect('/api/dummy/')
        else:
            self.response.set_status(403)
            self.response.out.write('Password is not correct')

class UploadCover(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        imdbid = self.request.get('imdbid')
        hexhash = self.request.get('hexhash')
        if not imdbid or not hexhash:
            logging.error("CoverUpload: imdbid('%s') or hexhash('%s') not present in request" % (imdbid, hexhash))
            self.set_status(500)
            return
        
        info = ImdbInfo.get_by_key_name(imdbid)
        if not info: 
            logging.error("CoverUpload: imdbinfo for id '%s' does not exist" % imdbid)
            blobstore.delete(upload.key())
            self.redirect('/api/dummy/')
            return
            
        i = Cover.get_by_key_name(hexhash)
        if i:
            logging.warning("CoverUpload: hash('%s') of new upload with imdb id('%s') already present" % (hexhash, imdbid))
            blobstore.delete(upload.key())
            self.redirect('/api/dummy/')
            return
        
        i = Cover(key_name=hexhash, imdbinfo=info)
        i.blobkey = upload.key()
        i.imdbid = imdbid
        
        i.put()
        logging.info("CoverUpload: uploaded cover with imdbid: %s" % imdbid)
        
        self.redirect('/api/dummy/')
        
    def get(self):
        if self.request.get('secret') == 'e8aAqE7pFcKjuTnAoTe4':
            upload_url = blobstore.create_upload_url('/upload_cover')
            if self.request.get('simple') == 'true':
                self.response.out.write(upload_url)
            else:
                self.response.out.write('<html><body>')
                self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
                self.response.out.write("""Upload File: <input type="file" name="file"><br><input type="text" value="test" name="test_name"><br> <input type="submit" 
                    name="submit" value="Submit"> </form></body></html>""")
        else:
            self.response.set_status(403)
            self.response.out.write('Password is not correct')
            
            
            
            
            
