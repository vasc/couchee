#!/usr/bin/python

from nntplib import NNTP
from nntpextensions import NNTPExtensions
import re
#from multiprocessing import Pool
from pymongo import Connection, DESCENDING
from Queue import Queue as queue
import Queue
from threading import Thread


def dict_group(news, name):
    resp = news.group(name)
    group = {}
    group['response'] = resp[0]
    group['count'] = int(resp[1])
    group['first'] = int(resp[2])
    group['last'] = int(resp[3])
    group['name'] = resp[4]
    return group

#def parse_header(header):
#    header_dict = {}
#    for l in header:
#        m_date = re.match('Date: (.*)$', l)
#        m_author = re.match('From: (.*)$', l)
#        m_msgid = re.match('Message-ID: (.*)$', l)
#        m_subject = re.match('Subject: (.*)$', l)
#        if m_date: header_dict['date'] = m_date.group(1)
#        elif m_author: header_dict['author'] = m_author.group(1)
#        elif m_msgid: header_dict['_id'] = m_msgid.group(1)
#        elif m_subject: header_dict['subject'] = m_subject.group(1)
#    if not ('date' in header_dict and 'author' in header_dict and '_id' in header_dict and 'subject' in header_dict):
#        raise Exception('Malformed response')
#    m_snum = re.match('(.*) \((\d+)/(\d+)\)$', header_dict['subject'])
#    if m_snum:
#       #header_dict['file_num'] = m_snum.group(1)
#        #header_dict['file_total'] = m_snum.group(2)
#        header_dict['file_id'] = m_snum.group(1)
#       header_dict['part_num'] = m_snum.group(2)
#       header_dict['part_total'] = m_snum.group(3)
#    else: raise Exception('Malformed subject: %s' % header_dict['subject'])
#    return header_dict

class KeyboardInterruptError(Exception): pass

def worker(work_group):
    while(True):
        try:
            workload = work_group.get(False)
        except Queue.Empty:
            return

        (init, end, group_name) = workload
        print 'running worker %s:%s' % (init, end)
        try:
            news = NNTPExtensions('eu.news.astraweb.com', user='vasc', password='dZeZlO89hY6F')
            group = dict_group(news, group_name)
            db = Connection().usenet
            resp, headers = news.xzver(str(init), str(end))
            #print "worker:\t\t%s\n\t\t%s" % (resp, headers)
            for h in headers:
                if re.search("\.nzb[\'\"\s\)\]]", h[1]):
                    header = {'group': group_name,
                              '_id': h[4],
                              'num': h[0],
                              'subject': h[1],
                              'date': h[3]}
                    try:
                        db.headers.insert(header)
                    except: continue
                    print '%s - %s...' % (h[0], h[1][:100])
            #print "init: %s, end: %s" % (init, end)
            db.control.update({"init": init, "end": end, "group": group_name}, {"$set": {"done": True}}, multi=True)
            #print 'Done :)'
            news.quit()
        except Exception as e: print e

def add_new_jobs(group_name):
    db = Connection().usenet
    max_h = db.control.find({"group": group_name}).sort('end', DESCENDING).limit(1)[0]['end'] + 1
    if not max_h: max_h = 0

    news = NNTP('eu.news.astraweb.com', user='vasc', password='dZeZlO89hY6F')
    group = dict_group(news, group_name)
    news.quit()

    i = max(group['first'], max_h)

    if max_h > group['last']: return
    while(i+10000 < group['last']):
        db.control.insert({'init': i, 'end': i+9999, 'done':False, "group": group_name})
        i += 10000

    db.control.insert({'init': i, 'end': group['last'], 'done':False, "group": group_name})


def main(group_name):
    add_new_jobs(group_name)

    db = Connection().usenet
    while db.control.find({"done": False, "group": group_name}).count() > 0:
        work_group = queue()
        try:
            count = 0
            for r in db.control.find({"done": False, "group": group_name}):
                count += 1
                work_group.put([r['init'], r['end'], group_name])

            threads = map(lambda x: Thread(name='thread_'+str(x), target=worker, args=(work_group,)), range(10))
            for t in threads: t.start()
            for t in threads: t.join()

            #p.apply_async(worker, [r['init'], r['end'], group_name])
            #p.close()
            #p.join()
        except KeyboardInterruptError:
            print 'Keyboard ^_^'
            #p.terminate()



if __name__ == '__main__':
    main(group_name = 'alt.binaries.teevee')

