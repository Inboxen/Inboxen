/*!
 * Copyright (c) 2015, 2018 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/main/LICENSE)
 */

(function($, window) {
    'use strict';
    var data;

    window.snippet = async function(snip) {
        var output;
        if (data === undefined) {
            var url = $("#snippetLink").attr("href");
            await fetch(url, {method: "GET"})
                .then(function(resp) {
                    return resp.json();
                })
                .then(function(json_data) {
                    data = json_data;
                });
        }
        output = data[snip];
        if (output === undefined) {
            throw "Snippet not found!";
        }
        return output;
    };
})(jQuery, window);

(function($){
    'use strict';

    $.fn.inboxenSpinnerToggle = function() {
        // disable or re-enable buttons to prevent over eager users from double
        // submitting, as well as giving some visual feedback that something is
        // happening

        this.each(function() {
            var $this = $(this);

            if ($this.is("form")) {
                // special case as forms disappear after success
                $this.data("clicked", "yes")
                    .find("button")
                        .prop("disabled", true)
                        .addClass("disabled")
                        .children("span.fa")
                            .addClass("fa-spinner fa-spin");
                $this.find("a.btn").addClass("disabled");
            } else if ($this.data("clicked") === "yes") {
                // reset button to default state
                $this.data("clicked", "no")
                    .prop("disabled", false)
                    .removeClass("disabled")
                    .children("span.fa")
                        .removeClass("fa-spinner fa-spin");
            } else {
                // disable button and replace icon with a spinner
                $this.data("clicked", "yes")
                    .prop("disabled", true)
                    .addClass("disabled")
                    .children("span.fa")
                        .addClass("fa-spinner fa-spin");
            }
        });

        return this;
    };

})(jQuery);

(function($) {
    'use strict';
    // alert close buttons, but only when JS is enabled
    window.snippet("close-alert-button").then(function(button) {
        $("div[role=alert]").each(function() {
            $(this).append(button);
        });
    });
})(jQuery);
