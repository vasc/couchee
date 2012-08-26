// Copyright (c) 2010 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// A generic onclick callback function.
function binsearchOnClick(info, tab) {

  var id = /\d{7}/, m = info.linkUrl.match(id);
  console.log(m);
  if(m){
      chrome.tabs.create({url: "http://binsearch.info/index.php?m=n&q=tt"+m[0]});
  }

}

// Create one test item for each context type.
//var contexts = ["page","selection","link","editable","image","video","audio"];
var context = "link";
var title = "Search in binsearch.com";
var id = chrome.contextMenus.create({title: title,
                                     contexts: [context],
                                     targetUrlPatterns: ["http://*.imdb.com/title/*"],
                                     onclick: binsearchOnClick});

console.log("'" + context + "' item:" + id);


//Page action

function checkForValidUrl(tabId, changeInfo, tab) {
    // If the letter 'g' is found in the tab's URL...
    var link = /imdb.*\/title\/(tt\d{7})/;
    var m = tab.url.match(link);
    if (m) {
        // ... show the page action.
        chrome.pageAction.show(tabId);
        var xhr = new XMLHttpRequest();
        xhr.open("GET", 'http://coucheeb.appspot.com/api/nzblink/'+m[1]+'/', true);
        id = m[1];
        xhr.onreadystatechange = function(){
            if (xhr.readyState == 4) {
                // JSON.parse does not evaluate the attacker's scripts.
                var resp = JSON.parse(xhr.responseText);
                console.log(resp);
                if(resp.length > 0){
                    localStorage[id] = xhr.responseText;
                    console.log(localStorage[id]);
                    chrome.pageAction.setIcon({tabId: tabId, path: 'favicon.ico'});
                    chrome.pageAction.setTitle({tabId: tabId, title: resp[0].rlsname});
                }
            }
        };
        xhr.send();
    }
}

function pageActionHandler(tab){
    link = /imdb.*\/title\/(tt\d{7})/;
    m = tab.url.match(link);
    if (m) {
        direct = localStorage[m[1]];
        console.log(direct);
        if(direct){
            chrome.tabs.create({url: JSON.parse(direct)[0].nzblink});
        }
        else{
            binsearchOnClick({linkUrl: tab.url}, tab);
        }
    }
}

chrome.pageAction.onClicked.addListener(pageActionHandler);
chrome.tabs.onUpdated.addListener(checkForValidUrl);

chrome.extension.onConnect.addListener(function(port) {
	port.onMessage.addListener(function(request){
		var id = request.id;
		var xhr = new XMLHttpRequest();
		xhr.open("GET", 'http://coucheeb.appspot.com/api/nzblink/'+id+'/', true);
		xhr.onreadystatechange = function(){
		    port.postMessage({id: id, response: xhr.responseText});
		    //console.log(xhr.responseText);
		};
		xhr.send();
	});
});

