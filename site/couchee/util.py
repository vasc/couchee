from datetime import datetime

def pretty_date(time):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    diff = now - time

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "1 day ago"
    return str(day_diff) + " days ago"
    
    
    
def make_pagination(current_page, total_pages, menu_pages, url_prefix):
    min_page = max(1, current_page - menu_pages/2)
    max_page = min(total_pages, min_page + menu_pages)
    
    first = not min_page == 1
    last = not max_page == total_pages
    
    menu = {'pages': []}
    if first: menu['first'] = {'url': url_prefix+'1', 'html': 'first'}
    if last: menu['last'] = {'url': url_prefix+str(total_pages), 'html': 'last'}
    
    
    for i in xrange(min_page, max_page+1):
        menu['pages'].append({'url': url_prefix+str(i), 'html': i})
        
    return menu











