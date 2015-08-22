/*
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */
function AreWeReadyYet(apiUrl) {
    var http = new XMLHttpRequest();
    http.open("HEAD", apiUrl, true);
    http.onload = function (e) {
        if (http.readyState > 2) {
            if (http.status == 202) {
                // not done
                document.getElementById("refreshnote").innerHTML = "";
            } else if (http.status == 201) {
                // done!
                clearInterval(timer);
                document.getElementById("refreshnote").innerHTML = "Loading results…";
                location.reload(true);
            } else if (http.status == 400) {
                clearInterval(timer);
                document.getElementById("searchinfo").innerHTML = "The search timed out. Please try again.";
                document.getElementById("searchinfo").className = "alert alert-warning";
                console.error("Server says there is no such search");
            } else {
                clearInterval(timer);
                document.getElementById("searchinfo").innerHTML = "Something went wrong while searching. Please try again later.";
                document.getElementById("searchinfo").className = "alert alert-danger";
                console.error("Unexpected response code");
            }
        }
    };
    http.send(null);
}
$(document).ready(function() {
    var element = document.getElementById("refreshnote");
    if (element === null) {
        return;
    }
    element.innerHTML = "";
    var apiUrl = $("#searchapiurl").data("url");
    // poll the server every 7000 ms
    var timer = setInterval(function(apiUrl){AreWeReadyYet(apiUrl);}, 7000);
});
