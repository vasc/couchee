import urllib2
from xml.dom.minidom import parseString, Node
from selectors import getElementsBySelector as sizzle
import tidy
import re

def download_info(year_start, year_end = None):
    if not year_end or year_end < year_start: year_start = year_end
    url = 'http://www.imdb.com/search/title?sort=num_votes,desc&title_type=feature&year=%s,%s&start=' % (year_start, year_end)
    start = 1
    
    votes = []
    rating = []
    
    while start <= 1000:
        f = urllib2.urlopen(url+str(start))
        html = f.read()
        html = re.sub(r"\&nbsp;", "", html)
        html = re.sub(re.compile(r'<script.*?</script>', re.S), "", html)
        #html = re.sub("\n", "", html)
        #print html
        
        ms = re.findall(r'<tr class="(?:(?:even)|(?:odd)) detailed">(.*?)</tr>', html, re.S)
        for m in ms:
            votes.append(int(re.sub(',', '', re.search(r'<td class="sort_col">(.*?)</td>', m).group(1))))
            rating.append(float(re.search(r'<span class="rating-rating">(.*?)<span>', m).group(1)))
        start += 50
        print start
    
    from pylab import scatter, show
    scatter(rating, votes, c='b', marker='o')
    show()



if __name__ == "__main__":
    download_info(2010)

