#!/usr/bin/python

import headers
from nzbs import organize, date, download, meta, upload
import os
import logging
import sys


if __name__ == "__main__":
    #print os.getcwd()
    #os.chdir('/home/vasco/projects/moviedatabase')
    logging.basicConfig(filename='/var/nzbs/nzbd.log',level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s')
    logging.info("Starting nzbd")
    #print os.getcwd()
    print "downloading headers...",
    sys.stdout.flush()
    headers.main(group_name = 'alt.binaries.teevee')
    headers.main(group_name = 'alt.binaries.moovee')
    print "done"
    print "organizing nzbs...",
    sys.stdout.flush()
    organize.organize_nzbs()
    print "done"
    print "tagging nzbs...",
    sys.stdout.flush()
    organize.tag_nzbs()
    print "done"
    #print "datting nzbs...",
    date.date_nzbs()
    #print "done"
    #print "downloading nzbs...",
    download.download_nzbs()
    meta.id_movies()

    upload.upload_nzbs()
    upload.publish_nzbs()

    meta.get_imdb_info()
    meta.download_posters()

    upload.movie_publish()
    upload.cover_publish()

    logging.info("Ending nzbd")
    #print "done"

