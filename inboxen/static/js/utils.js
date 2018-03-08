/*!
 * Copyright (c) 2018 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

(function($){
    'use strict';

    $.fn.inboxenSpinnerToggle = function() {
        //

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
