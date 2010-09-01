#!/usr/bin/python

import pymongo
import gzip
import sys
from datetime import datetime as d
import nzbs.download
import os
import re
from lxml import objectify

def main(nzb_file):
    m = re.search(r'/([^/]*$)', nzb_file)
    if m: filename = m.group(1)
    else: filename = nzb_file

    rlsname = filename[:-4]
    nzb = {'category': 'moovee'}
    f = open(nzb_file, 'r')
    date = d.fromtimestamp(int(objectify.parse(f).getroot().file.attrib['date']))
    f.seek(0)
    
    folder = nzbs.download.get_folder(nzb)
    fgz = gzip.open(os.path.join(folder, filename+'.gz'), 'wb')
    fgz.write(f.read())
    f.close()
    fgz.close()
    
    nzb['_id'] = rlsname
    nzb['rlsname'] = rlsname
    nzb['tags'] = ['#a.b.moovee@EFNet', 'ByHand']
    nzb['stages'] = {'downloaded': True}
    nzb['stage'] = 2
    nzb['date'] = date
    nzb['file'] = filename+'.gz'
    
    pymongo.Connection().usenet.nzbs.save(nzb)


if __name__ == '__main__':
    main(sys.argv[1]) 
