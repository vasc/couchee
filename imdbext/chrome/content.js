link = /^\/title\/(tt\d{7})\/$/;

function response(data){
    r = JSON.parse(data['response']);
    if(r.length > 0){
        el = $('[data-couchee='+data['id']+']');
        newel = $('<a href="'+ r[0].nzblink +'" title="' + r[0].rlsname + '"><img src="'+ chrome.extension.getURL("favicon.ico") + '" /></a>');
        newel.css('padding-left', '6px');
        newel.css('vertical-align', 'middle');

        el.after(newel);
    }
}

$('[href*=title]:not(:has(img))').each(function(index, el){
    el = $(el);
    m = el.attr('href').match(link);
    if(m){
        id = m[1];
        el.attr('data-couchee', id);
        chrome.extension.sendRequest({'action' : 'getNzbLink', 'id': id},  response);
    }
});

