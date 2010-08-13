import pymongo

header = u"""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Teevee</title>
        <link rel="stylesheet" href="site/css/main.css" type="text/css" />
    </head>
    <body id="index" class="home">
        <ul id="shows_list">"""
            
footer = u"""        </ul>
    </body>
</html>"""

db = pymongo.Connection().imdb

count = 1

print header

for movie in db.movies.find():
    print u'<li>%4d. <span class="title">%s %s</span><span class="meta">%.1f %s</span> <a href="#" class="link">[nzb]</a></li>' % (count, movie['name'], movie['year'], movie['rating'], movie['votes'])
    count += 1   
    
print footer
