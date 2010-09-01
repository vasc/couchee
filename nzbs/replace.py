import pymongo

db = pymongo.Connection().usenet

for nzb in db.nzbs.find():
    if 'stages' in nzb:
        s = {}
        for a in nzb['stages']:
            s[a] = True
        nzb['stages'] = s
        print db.nzbs.save(nzb)
