#!/usr/bin/python

import headers
from nzbs import organize, date, download, meta
import os
import logging


if __name__ == "__main__":
    #print os.getcwd()
    #os.chdir('/home/vasco/projects/moviedatabase')
    logging.basicConfig(filename='nzbd.log',level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s')
    logging.info("Starting nzbd")
    #print os.getcwd()
    #print "downloading headers...",
    headers.main(group_name = 'alt.binaries.teevee')
    headers.main(group_name = 'alt.binaries.moovee')
    #print "doen"
    #print "organizing nzbs...",
    organize.organize_nzbs()
    #print "done"
    #print "tagging nzbs...",
    organize.tag_nzbs()
    #print "done"
    #print "datting nzbs...",
    date.date_nzbs()
    #print "done"
    #print "downloading nzbs...",
    download.download_nzbs()
    meta.id_movies()
    logging.info("Ending nzbd") 
    #print "done"
