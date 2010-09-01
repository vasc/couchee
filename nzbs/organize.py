import pymongo
import re
import logging


def organize_nzbs():
    db = pymongo.Connection().usenet
    r = re.compile(r'\((\d+)\\(\d+)\)\s*$')
    for h in db.headers.find():
        m = re.search(r'(.*)\((\d+)\/(\d+)\)\s*$', h['subject'])
        if m:
            c = False
            name = m.group(1)
            part = m.group(2)
            total = m.group(3)
            nzb = db.nzbs.find_one({'_id': name})
            if not nzb:
                c = True
                nzb = {'_id': name,
                       'total': total,
                       'group': h['group'],
                       'articles': [], 
                       'stage': 0,
                       'stages': {}
                      }
            article = {'msgid': h['_id'], 'part': part, 'date': h['date']}
            nzb['articles'].append(article)
            db.nzbs.save(nzb)
            if c: s = "Created"
            else: s= "Updated"
            logging.info("%s nzb: %s" % (s, nzb['_id']))
        db.headers.remove({'_id': h['_id']})

def movie_tag(nzb, db):
    m = re.search(r'\s*\[\s*#altbin\s*@\s*EFNet\s*\]\s*-?\s*\[\s*Full\s*\]', nzb['_id'], re.I)
    if nzb['group'] == 'alt.binaries.movies.divx' and m:
        if not 'tags' in nzb: nzb['tags'] = []
        nzb['tags'].append('#altbin@EFNet')
        nzb['stage'] = 1
        db.nzbs.save(nzb)
        logging.info("Tagged %s as '#altbin@EFNet'" % nzb['_id'])

def moovee_tag(nzb, db):
    m = re.search(r'\s*\[\s*FULL\s*\]\s*-?\s*\[\s*#a.b.moovee@EFNet\s*\]\s*-?\s*\[\s*([^\s\]]*)\s*\]', nzb['_id'], re.I)
    if not m: m = re.search(r'\s*\[\s*#a.b.moovee@EFNet\s*\]\s*-?\s*\[\s*FULL\s*\]\s*-?\s*\[\s*([^\s\]]*)\s*\]', nzb['_id'], re.I)
    
    if nzb['group'] == 'alt.binaries.moovee' and m:
        nzb['rlsname'] = m.group(1)
        if not 'tags' in nzb: nzb['tags'] = []
        nzb['tags'].append('#a.b.moovee@EFNet')
        nzb['category'] = 'moovee'
        nzb['stage'] = 1
        nzb['stages']['tagged'] = True
        db.nzbs.save(nzb)
        logging.info("Tagged %s as '#a.b.moovee@EFNet'" % nzb['rlsname'])


def tv_tag(nzb, db):
    m = re.search(r'\s*\[\s*FULL\s*\]\s*-?\s*\[\s*#a.b.teevee@EFNet\s*\]\s*-?\s*\[\s*([^\s\]]*)\s*\]', nzb['_id'], re.I)
    if not m: m = re.search(r'\s*\[\s*#a.b.teevee@EFNet\s*\]\s*-?\s*\[\s*FULL\s*\]\s*-?\s*\[\s*([^\s\]]*)\s*\]', nzb['_id'], re.I)
    if nzb['group'] == 'alt.binaries.teevee' and m:
        nzb['rlsname'] = m.group(1)
        if not 'tags' in nzb: nzb['tags'] = []
        nzb['tags'].append('#a.b.teevee@EFNet')
        nzb['category'] = 'teevee'
        nzb['stage'] = 1
        nzb['stages']['tagged'] = True
        db.nzbs.save(nzb)
        logging.info("Tagged %s as '#a.b.teevee@EFNet'" % nzb['rlsname'])
        
def tag_nzbs():
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'stage': 0}):
        #movie_tag(nzb, db)
        tv_tag(nzb, db)
        moovee_tag(nzb, db)
