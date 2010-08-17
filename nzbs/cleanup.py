def max_date(a1, a2):
    if parse_date(a1['date']) > parse_date(a2['date']): return a1
    else: return a2
    

def clean_nzbs():
    """Needs lots of testing, should clean nzbs with repeated articles
    it does so, but with some bugs
    """
    locale.setlocale(locale.LC_TIME, "en_GB.utf8")
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'stage': 0}):
        cleaned_articles = []
        dirty = False
        if not int(nzb['total']) == len(nzb['articles']): print 'to clean'
        for i in range(1, int(nzb['total'])+1):
            articles = [a for a in nzb['articles'] if int(a['part']) == i]
            if len(articles) == 0:
                print "error", nzb['articles']
                continue
            elif len(articles) > 1:
                r = reduce(max_date, articles, {'date': datetime(1900, 1, 1).strftime('%d %b %Y %H:%M:%S GMT')})
                cleaned_articles.append(r)
                dirty = True
            else:
                cleaned_articles.append(articles[0])
                
        print len(cleaned_articles), '?', len(nzb['articles']), '<=', dirty
        if (not dirty) or (not int(nzb['total']) == len(cleaned_articles)): 
            continue
        nzb['articles'] = cleaned_articles
        print 'cleaned: ', nzb['_id']
