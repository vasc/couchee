tmdb = TMDB(API_KEY, 'xml', 'en')
data = tmdb.searchResults('james bond')
people = tmdb.personResults('adam sandler')
person = tmdb.person_getInfo(TMDB_PERSON_ID)
movie_info = tmdb.getInfo(TMDB_MOVIE_ID)
imdb_data = tmdb.imdbResults(IMDB_TTID)
imdb_images = tmdb.imdbImages(IMDB_TTID)
tmdb_images = tmdb.tmdbImages(TMDB_MOVIE_ID)
