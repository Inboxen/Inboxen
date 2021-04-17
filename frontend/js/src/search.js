/*!
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/main/LICENSE)
 */

(function($) {
    'use strict';
    var timer;

    function areWeReadyYet($refreshNote, $searchInfo, timer) {
        var http = new XMLHttpRequest();
        http.open("HEAD", $refreshNote.data("url"), true);
        http.onload = function (e) {
            if (http.readyState > 2) {
                if (http.status == 202) {
                    // not done
                    $refreshNote.html("");
                } else if (http.status == 201) {
                    // done!
                    clearInterval(timer);
                    window.snippet("search-loading-text").then(function(text) {
                        $refreshNote.html(text);
                    }).finally(function() {
                        location.reload(true);
                    });
                } else if (http.status == 400) {
                    clearInterval(timer);
                    window.snippet("search-timed-out").then(function(text) {
                        $searchInfo.html(text);
                        console.error("Server says there is no such search");
                    });
                } else {
                    clearInterval(timer);
                    window.snippet("generic-error").then(function(error) {
                        $searchInfo.replaceWith(error);
                        console.error("Unexpected response code");
                    });
                }
            }
        };
        http.send(null);
    }

    var $refreshNote = $("#search-refreshnote");
    var $searchInfo = $("#search-info");

    $("#inboxen-search-box").on("submit", function() {
        window.location = this.action + this.q.value + "/";
        return false;
    });

    if ($refreshNote.length !== 0) {
        $refreshNote.html("");
        // poll the server every 7000 ms
        timer = setInterval(function(){areWeReadyYet($refreshNote, $searchInfo, timer);}, 7000);
    }
})(jQuery);
