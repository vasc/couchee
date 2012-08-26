#!/usr/bin/python

import argparse
import re
import os
import shutil
import gzip

from xml.dom.minidom import parse, parseString


def main():
	parser = argparse.ArgumentParser(description='download tv show')

	
	parser.add_argument('--nzbslocation', dest='location', default='/var/nzbs/teevee/')
	parser.add_argument('--downloadlocation', dest='download', default='/home/vasco/nzbs/')
	parser.add_argument('-d', '--download', dest='run', action='store_true')
	parser.add_argument('--size', action='store_true')

	media = parser.add_mutually_exclusive_group()
	media.add_argument('--dvd', action='store_true', help='search only dvd')
	media.add_argument('-t', '--tv', action='store_true', help='search only tv')

	hd = parser.add_mutually_exclusive_group()
	hd.add_argument('-s','--sd', action='store_true', help='search only sd')
	hd.add_argument('-x', '--hd', action='store_true', help='search only hd')

	parser.add_argument('expr', nargs='+')

	args = parser.parse_args()

	filters = args.expr
	if args.hd: filters.append('x264')
	if args.sd: filters.append('xvid')
	if args.tv: filters.append('hdtv')
	if args.dvd: filters.append('dvdrip')

	for show in sorted(filter(make_match(filters), os.listdir(args.location))):
		path = os.path.join(args.location, show)
		if args.run:
			shutil.copy(path, args.download)
			print 'downloading %s' % show
		elif args.size:
			print '%s %s' % (show, hsize(nzbsize(path))) 
		else:
			print show


def make_match(args):
	compiled_args = [re.compile(arg, re.I) for arg in args]
	
	def match(path):
		return all([arg.search(path) for arg in compiled_args])
	return match


def nzbsize(path):
	f = gzip.open(path, 'r')
	dom = parseString(f.read())
	return sum([int(e.getAttribute('bytes')) for e in dom.getElementsByTagName('segment')])

def hsize(num):
	for x in ['bytes','KB','MB','GB','TB']:
		if num < 1024.0:
			return "%3.1f%s" % (num, x)
		num /= 1024.0

if __name__ == "__main__":
	main()
