import glob
import os
import pprint
import re

def main(dir):
  def filelist(r):
      for root, dirnames, filenames in os.walk(r):
          for filename in filenames: 
              if re.search('\.avi$', filename): yield filename
          for dirname in dirnames: filelist(os.path.join(root, dirname))
 
  shows = filelist(dir)
  shows = filter(lambda x: not re.search('sample', x), shows)
  shows = map(lambda x: x.lower(), shows)
  m1 = map(lambda x: re.search('^(.*?)[\._]s(\d\d)e(\d\d)[\._]', x), shows)
  m2 = map(lambda x: re.search('^(.*?)[\._](\d+)(\d\d)[\._]', x), shows)
  
  shows = [m.groups() for m in map(lambda x: x[not bool(x[0])], zip(m1, m2)) if m]
  s = dict(reduce(lambda s, x: s + [(x[0], [])], shows, []))
  for show in shows: s[show[0]].append(show[1:])
  
  pprint.pprint(s)



if __name__ == '__main__':
  main('/media/B652AAB052AA7531/Users/Public/Videos/Shows/')
