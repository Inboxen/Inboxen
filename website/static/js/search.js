/*
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */
function AreWeReadyYet($refreshNote, $searchInfo, timer) {
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
                $refreshNote.html("Loading results…");
                location.reload(true);
            } else if (http.status == 400) {
                clearInterval(timer);
                $searchInfo.html("The search timed out. Please try again.");
                $searchInfo.addClass("alert alert-warning");
                console.error("Server says there is no such search");
            } else {
                clearInterval(timer);
                $searchInfo.html("Something went wrong while searching. Please try again later.");
                $searchInfo.addClass("alert alert-warning");
                console.error("Unexpected response code");
            }
        }
    };
    http.send(null);
}
$(document).ready(function() {
    var $refreshNote = $("#refreshnote");
    var $searchInfo = $("#searchinfo");
    if ($refreshNote.length === 0) {
        return;
    }
    $refreshNote.html("");
    // poll the server every 7000 ms
    var timer = setInterval(function(){AreWeReadyYet($refreshNote, $searchInfo, timer);}, 7000);
});
