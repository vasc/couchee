import locale
import pymongo
import logging
import re
from datetime import datetime, timedelta


def date_nzbs():
    locale.setlocale(locale.LC_TIME, "en_GB.utf8")
    db = pymongo.Connection().usenet
    for nzb in db.nzbs.find({'date': None}):
        if not 'date' in nzb:
            if 'rlsname' in nzb: id = 'rlsname'
            else: id = '_id'
            date = nzb['articles'][0]['date']
            d = parse_date(date)
            if not d:
                logging.error("Unable to parse date: %s from %s" % (nzb[id], date))
            else:
                nzb['date'] = d
                logging.info("Dated %s: %s" % (nzb[id], nzb['date']))
                db.nzbs.save(nzb)

def parse_date(date):
    tzd = re.search("[-+](\d\d)(\d\d)$", date)
    d = try_date(date, "%d %b %Y %H:%M:%S %Z")        
    if not d:
        d = try_date(date, "%a, %d %b %Y %H:%M:%S %Z")
    if not d and tzd:
        d = try_date(date[:-6], "%a, %d %b %Y %H:%M:%S")
        if not d: d = try_date(date[:-6], "%d %b %Y %H:%M:%S")
        if d:
            td = timedelta(hours=int(tzd.group(1)), minutes=int(tzd.group(2)))
            if date[-5] == '+': d = d - td
            else: d = d + td
            print '%s => %s' % (date, d)
    return d        
                    
def try_date(date, format):
    try:
        d = datetime.strptime(date, format)
    except ValueError:
        d = None
    return d

