#!/usr/bin/python

import headers
import nzbs
import os
import logging

if __name__ == "__main__":
    #print os.getcwd()
    os.chdir('/home/vasco/projects/moviedatabase')
    logging.basicConfig(filename='nzbd.log',level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s')
    logging.info("Starting nzbd")
    #print os.getcwd()
    #print "downloading headers...",
    headers.main(group_name = 'alt.binaries.teevee')
    headers.main(group_name = 'alt.binaries.moovee')
    #print "doen"
    #print "organizing nzbs...",
    nzbs.organize_nzbs()
    #print "done"
    #print "tagging nzbs...",
    nzbs.tag_nzbs()
    #print "done"
    #print "datting nzbs...",
    nzbs.date_nzbs()
    #print "done"
    #print "downloading nzbs...",
    nzbs.download_nzbs()
    logging.info("Ending nzbd") 
    #print "done"
