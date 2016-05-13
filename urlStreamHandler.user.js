// ==UserScript==
// @name        URL Stream Handler
// @namespace   be.kuleuven.cs.dtai
// @description Send visited urls to local server and show most likely links.
// @version     1
// @require     http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js
// @grant       GM_xmlhttpRequest
// @grant       GM_addStyle
// @run-at      document-end
// ==/UserScript==

try {
  var toppage = (window.top == window.self);
  if (!toppage) {
    return;
  }

  var url = window.location.href;

  var send = function(data, onload) {
    data.ts = (new Date()).toISOString();
    data_string = JSON.stringify(data);
    GM_xmlhttpRequest({
      method: "POST",
      url: "http://localhost:8000",
      data: data_string,
      headers: {
        "Content-Type": "application/json",
        "Content-Length": data.length
      },
      onerror: function(error) {
          console.log(data_string);
        console.log('Calling urlStreamHandler failed', error);
      },
      onload: onload
    });
  };

  // Associate a click event with all links
  var addClickEvent = function(element) {
    if (element.dataset.dtaitracked) {
      return;
    }
    element.dataset.dtaitracked = true;
    element.addEventListener('click', function(link) {return function(event) {
      try {
        var href = '';
        if (link.href !== undefined) {
          href = link.href;
        }
        send({
          "action": "click",
          "target": href,
          "url": url,
        });
      } catch (e) {
        console.log('An error occured in a click listener', e);
      }
    };}(element));
  };
  for (var i=0; i<document.links.length; i++) {
    addClickEvent(document.links[i]);
  }
  var observer = new MutationObserver(function(mutations) {
    try {
      mutations.forEach(function(mutation) {
        try {
          var node;
          for (var i=0; i<mutation.addedNodes.length; i++) {
            node = mutation.addedNodes[i];
            if (node.tagName === "A" || node.tagName === "a") {
              addClickEvent(node);
            } else if (node.getElementsByTagName) {
              var atags = node.getElementsByTagName('a');
              for (var aidx=0; aidx<atags.length; aidx++) {
                addClickEvent(atags[aidx]);
              }
            }
          }
        } catch (e) {
          console.log('An error occured processing added nodes', e);
        }
      });
    } catch (e) {
      console.log('An error occured after a mutation change', e);
    }
  });
  observer.observe(document.body, {childList:true, subtree:true});


  // Window events
  // Possible events include hashchange, pageshow, popstate, beforeunload
  window.addEventListener('beforeunload', function(event) {
    send({
      "action": 'beforeunload',
      "url": url
    });
  });

  // Catch any other changes by polling the location
  setInterval(function() {
    try {
      if(location.href !== url) {
        send({
          "action": 'polling',
          "url": location.href,
        });
        url = location.href;
      }
    } catch (e) {
      console.log('An error occured while processing polled change', e);
    }
  }, 500);

  // Send current page load and react to result
  var html = '';
  if (document.body) {
    html = document.body.innerHTML;
  }
  send({
    "action": "load",
    "url": url,
    "top": toppage,
    "html": html
  }, function(response) {
    try {
      // Message to show the python part ran without errors
      console.log("Predictive webbrowsing is active.");

      // Loading in style elements
      // Loading in through external css file only works on non-https websites
      /*GM_addStyle('#ml_suggestionbox {'+
        'position:fixed;bottom: 0;right: 0;'+
        'width:230px;height: 20px;border:1px solid #ffffff;'+
        'background-color:#333;'+
        'padding: 15px 5px 10px 25px;'+
        '-moz-box-shadow:-8px 8px 20px -6px #000;'+
        '-webkit-box-shadow:-8px 8px 20px -6px #000;'+
        'box-shadow:-8px 8px 20px -6px #000;'+
        '-moz-border-radius-topleft: 25px;'+
        '-webkit-border-top-left-radius: 25px;'+
        'border-top-left-radius: 25px;'+
        '-webkit-transition: height .5s ease;'+
        '-moz-transition: height .5s ease;'+
        '-ms-transition: height .5s ease;'+
        '-o-transition: height .5s ease;'+
        'transition: height .5s ease;}');
      GM_addStyle('#ml_suggestionbox:hover{height: 150px;}');
      GM_addStyle('#ml_suggestionbox.expanded {height: 150px;}');
      GM_addStyle('#ml_suggestionbox h3{color: #f5f5f5;margin:0px;}');
      GM_addStyle('#ml_suggestionbox .suggestions {'+
        'display: none;color: #eee;list-style: disc;'+
        'margin-left: 15px;padding: 8px;position: relative;'+
        '-webkit-transition: display .5s ease;'+
        '-moz-transition: display .5s ease;-ms-transition: display .5s ease;'+
        '-o-transition: display .5s ease;transition: display .5s ease;}');
      GM_addStyle('#ml_suggestionbox.expanded .suggestions,'+
      '#ml_suggestionbox.popup .suggestions{display: block;}');
      GM_addStyle('#ml_suggestionbox a,#ml_suggestionbox a:link,'+
      '#ml_suggestionbox a:vistited {color: #eee !important;'+
      'text-decoration: none !important;}');
      GM_addStyle('#ml_suggestionbox a:hover,'+
      '#ml_suggestionbox a:active {color: #f5f5ff;'+
      'border-bottom: 1px solid #ffffff;text-decoration: none;}');*/
    GM_addStyle('#ml_suggestionbox {'+
    'font-size:13px;'+
    'width: 0px;background: #f5f5f5;'+
    'color: #888;position: fixed;right:0;top: 106px;z-index: 10000;'+
    '-webkit-transition: all .8s ease;'+
    '-moz-transition: all .8s ease;'+
    '-ms-transition: all .8s ease;'+
    '-o-transition: all .8s ease;'+
    'transition: all .8s ease;}');
    GM_addStyle('#ml_suggestionbox.expanded,#ml_suggestionbox:hover {'+
    'width: 200px;right: -200px;}');
    GM_addStyle('#ml_suggestionbox * {'+
    '-moz-box-sizing: content-box;'+
    '-webkit-box-sizing: content-box;box-sizing: content-box;}');
    GM_addStyle('#ml_inner {'+
    '-webkit-box-shadow: 0 2px 8px 2px rgba(0, 0, 0, .13);'+
    '-moz-box-shadow: 0 2px 8px 2px rgba(0, 0, 0, .13);'+
    'box-shadow: 0 2px 8px 2px rgba(0, 0, 0, .13);'+
    'border: 1px solid rgba(23, 24, 25, .14);visibility: hidden;}');
    GM_addStyle('#ml_suggestionbox ul.suggestions {'+
    'list-style: none;padding-left: 0px;margin-left: 0px;text-align: left;}');
    GM_addStyle('#ml_suggestionbox ul.suggestions li {'+
    'margin-top:5px;width:250px;}');
    GM_addStyle('#ml_suggestionbox a {'+
    'color: #333;text-decoration: none;'+
    'width: 250px;padding: 3px 10px 3px 3px;}');
    GM_addStyle('#ml_suggestionbox .suggestions li a:hover,'+
    '#ml_suggestionbox .suggestions li a:active {'+
    'color: #888;border-bottom: 1px solid #888;text-decoration: none;}');
    GM_addStyle('#ml_suggestionbox .title {'+
    'padding: 15px;background-color: #343436;'+
    'font-size:15px; color: #e6e6e6;'+
    'font-family: "Lato", "Helvetica Neue", Helvetica, Arial, sans-serif;}');
    GM_addStyle('#ml_suggestionbox .switcher-title {'+
    'font-size: 12px;font-family: Raleway, Arial, Helvetica, sans-serif;'+
    'height: 38px;line-height: 38px;'+
    'text-align: center;border-top: 1px solid #fff;}');
    GM_addStyle('#ml_suggestionbox .switch-button {'+
    'width: 40px;height: 38px;'+
    'line-height: 38px;color: #f5f5f5;'+
    'position: absolute;top: 49px;'+
    'left: -41px;background: #343436;'+
    'cursor: pointer;font-size: 26px;'+
    'text-align: center;'+
    'font-family:"Times New Roman";'+
    'border: 1px solid #f5f5f5;text-decoration: none;'+
    'display: block;border: 1px solid #f5f5f5;'+
    '-webkit-box-shadow: 0 2px 8px 2px rgba(0, 0, 0, .13);'+
    '-moz-box-shadow: 0 2px 8px 2px rgba(0, 0, 0, .13);'+
    'box-shadow: 0 2px 8px 2px rgba(0, 0, 0, .13);'+
    'border: 1px solid rgba(23, 24, 25, .14);}');

      /*
       * Show response from script in back-end here
       * Response object contains:
       * - Response status (success True or False)
       * - Array with suggested URLs
       */
      data = JSON.parse(response.response);
      console.log(data);

      // Append the suggestion box
      $("body").append('<div id="ml_suggestionbox" class="expanded" style="right: 0px;">'+
            '<div id="ml_inner" style="visibility: visible;"></div></div>');

      if(!data.success)
        $("#ml_inner").append('<div class="title">No suggestions found</div>');
      else $("#ml_inner").append('<div class="title">Suggestions</div>');

      // Add the suggested links to suggestionbox

      var suggestions = "";
      $.each(data.guesses, function(index, val) {
        var name = val.replace("http://", "")
                         .replace("https://", "")
                         .split('/')[0];
        suggestions += '<li>';
        suggestions +='<a href="'+val+'" title="Full link: '+val+'">&#9830; ';
        suggestions += name + '</a></li>';
      });
      $("#ml_inner").append('<ul class="suggestions">'+suggestions+'</ul>');
      $("#ml_inner").append('<div class="switcher-title">'+
        '<a id="reset_styles" href="#" class="simple">Settings</a></div>');
      $("#ml_suggestionbox").append('<div class="switch-button">S</div>');
      // TODO: Do something (e.g. show a top bar with the final link of the
      //       suspected sequence)
      /*var best_guess = data.guesses[0][0];
      var l = document.links;
      for (var i=0; i<l.length; i++) {
        // As a simple example, we highlight the link with the highest
        // probability.
        if (l[i].href == best_guess) {
          l[i].style["background-color"]="yellow";
        }
    }*/

      // Helper function for showing on mouseover - together with CSS3
      $(function(){
          // Collapse box after some time to minimize distration
          setTimeout(function(){
              $('#ml_suggestionbox').removeClass("expanded")
            }, 3000);
        });

    } catch (e) {
      console.log('An error occured while processing the guesses', e);
    }
  });
} catch (e) {
  console.log('An error occured', e);
}
