/*
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

// adds event listeners for inline forms to be popped in
$(document).ready(function() {
    var $optionButtons = $("table#home td.inbox-options > a");

    $optionButtons.click(function() {
        var $this = $(this);
        var $row = $this.parents("tr:has(td.inbox-name)");
        var formURL = "/forms/inbox/edit/" + $row.attr("id") + "/";

        if (!$row.next().hasClass("inbox-edit-form-row")) {
            if ($this.data("clicked") === "yes") {
                return false;
            } else {
                $this.data("clicked", "yes");
                $this.addClass("disabled");
                setTimeout(function() {
                    $this.data("clicked", "no");
                    $this.removeClass("disabled");
                }, 3000);
            }

            $.get(formURL, function(data) {
                // double check
                if (!$row.next().hasClass("inbox-edit-form-row")) {
                    $row.after("<tr class=\"inbox-edit-form-row\"><td colspan=\"4\">" + data + "</td></tr>");
                }
            });
        } else if ($row.next().hasClass("inbox-edit-form-row")) {
            $row.next().remove();
        }
        return false;
    });
});
