/*!
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

function initForm($form) {
    var inbox = $form.data("inbox-selector");

    $form.submit(function(event) {
        event.preventDefault();
        var description, is_disabled, $this;

        $this = $(this);

        if ($this.data("sending") === "yes") {
            return false;
        }

        $this.find("button").prop("disabled", true);
        $this.find("a.btn").addClass("disabled");
        $this.data("sending", "yes");
        setTimeout(function() {
            $this.data("sending", "no");
            $this.find("button").prop("disabled", false);
            $this.find("a.btn").removeClass("disabled");
        }, 3000);

        description = $this.find("#id_description").val();
        is_disabled = $this.find("#id_disable_inbox").prop("checked");

        $.ajax({
            type: "POST",
            url: $this.attr('action'),
            data: $this.serializeArray(),
            complete: function(xhr, statusText) {
                var $row = $("#" + inbox + " + tr");

                if (xhr.status === 204) {
                    var $inbox_row = $("#" + inbox);
                    var $description_cell = $inbox_row.children("td.inbox-description");

                    $description_cell.text(description);

                    if (is_disabled && !$inbox_row.hasClass("inbox-disabled")) {
                        $inbox_row.addClass("inbox-disabled");
                        $inbox_row.find("td.inbox-name  span.label").remove();
                        $inbox_row.find("td.inbox-name").append("<span class=\"label label-default\" title=\"Inbox has been disabled\">Disabled</span>");
                    } else if (!is_disabled && $inbox_row.hasClass("inbox-disabled")) {
                        $inbox_row.removeClass("inbox-disabled");
                        $inbox_row.find("td.inbox-name span.label-default").remove();
                    }

                    $row.remove();
                } else {
                    var $form = $row.children("td");
                    if (xhr.status === 200) {
                        $form.html(xhr.responseText);
                    } else {
                        $form.html("<div class=\"alert alert-info\">Sorry, something went wrong.</div>");
                        console.log("Form for " + inbox + " failed to POST (" + xhr.status + ")");
                    }
                }
            }
        });
    });
    $("#form-" + inbox + " > a").click(function() {
        var $row = $("#" + inbox + " + tr");
        $row.remove();
    });
}

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
                    initForm($row.next().find("form"));
                }
            });
        } else if ($row.next().hasClass("inbox-edit-form-row")) {
            $row.next().remove();
        }
        return false;
    });
});
