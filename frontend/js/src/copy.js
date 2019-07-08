/*!
 * Copyright (c) 2018 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

(function($){
    'use strict';

    $.fn.inboxenInboxCopyBtn = function() {
        var copySupported;
        copySupported = document.queryCommandSupported("copy");

        if (!copySupported) {
            // we can't copy, so this plugin will do nothing
            return this;
        }

        this.each(function() {
            var $this, inboxNameSelector, buttonClasses,
                buttonContainerSelector, buttonText, buttonTitle,
                childrenSelector, inboxList;

            $this = $(this);
            inboxNameSelector = $this.data("inbox-name");
            buttonContainerSelector = $this.data("button-container");
            buttonClasses = $this.data("button-classes");
            buttonText = $this.data("button-text") || "";
            buttonTitle = $this.data("button-title") || "";
            childrenSelector = $this.data("children") || "";

            if (inboxNameSelector === undefined || buttonClasses === undefined || buttonContainerSelector === undefined) {
                console.error("Could not find required data- params");
                return;
            }

            if (childrenSelector) {
                // we're looking for a child element
                inboxList = $this.children(childrenSelector);
            } else {
                // we're looking all over the page
                inboxList = $(document);
            }

            inboxList.each(function () {
                var $this = $(this);
                // buttonTitle is also added to span.sr-only because screen
                // readers don't ever read the title attribute, but desktops
                // want it for tooltips
                var button = $("<button class='" + buttonClasses + "' title='" + buttonTitle +
                    "'><span class='fa fa-lg fa-clipboard' aria-hidden='true'></span>" +
                    "<span class='sr-only'>" + buttonTitle + "</span>" + buttonText + "</button>");
                var inboxName = $this.find(inboxNameSelector)[0];

                if (inboxName === undefined) {
                    // title row (probably)
                    return;
                } else if (inboxName.textContent.indexOf("@") === -1) {
                    // ignore unified inbox
                    return;
                }

                button.click(function (e) {
                    var selection = window.getSelection();
                    var range = document.createRange();

                    e.preventDefault();

                    range.selectNodeContents(inboxName);
                    selection.removeAllRanges();
                    selection.addRange(range);

                    document.execCommand("copy");

                    selection.removeAllRanges();
                });

                $this.find(buttonContainerSelector).prepend(button);
            });
        });

        return this;
    };

    $("#inbox-list").inboxenInboxCopyBtn();
    $("#email-list").inboxenInboxCopyBtn();

})(jQuery);
