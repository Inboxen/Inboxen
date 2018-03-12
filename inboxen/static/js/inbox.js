/*!
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

(function($) {
    'use strict';

    var important_label = '<span class="label label-danger" title="Message has been marked as important">Important</span>';

    function toggleImportant($row) {
        if ($row.find("span.label-danger").length === 0) {
           $row.find("div.email-flags").append(important_label);
        } else {
            $row.find("div.email-flags span.label-danger").remove();
        }
    }

    function markImportant($row) {
        if ($row.find("div.email-flags span.label-danger").length === 0) {
           $row.find("div.email-flags").append(important_label);
        }
    }

    function unmarkImportant($row) {
        $row.find("div.email-flags span.label-danger").remove();
    }

    function deleteRow($row) {
        $row.remove();
    }

    $("#email-list button[type=submit]").click(function(event) {
        event.preventDefault();

        var $this = $(this);
        if ($this.data("clicked") === "yes") {
            return false;
        }

        $this.inboxenSpinnerToggle();

        var button = {"name": $this.attr("name"), "value": $this.attr("value")};
        var form_data = $("#email-list").serializeArray();
        form_data.push(button);

        $.ajax({
            type: "POST",
            url: $("#email-list").data("url"),
            data: form_data,
            complete: function(xhr, statusText) {
                if (xhr.status === 204) {
                    var $row = $("#email-" + button.value);
                    // was the important toggle pressed?
                    if (button.name === "important-single") {
                        toggleImportant($row);
                    } else {
                        // multiple emails were selected
                        var fn;
                        if (button.name === "important") {
                            fn = markImportant;
                        } else if (button.name === "unimportant") {
                            fn = unmarkImportant;
                        } else if (button.name === "delete") {
                            fn = deleteRow;
                        } else {
                            // return early, I don't know what button was pressed
                            return;
                        }

                        $.each(form_data, function(index, value) {
                            if (value.value === "email") {
                                fn($("#email-" + value.name));
                            }
                        });
                    }
                } else {
                    var $messageBlock = $("#alertmessages");
                    var message = '<div class="alert alert-warning" role="alert">Something went wrong!<button type="button" class="close" data-dismiss="alert"><span class="fa fa-times" aria-hidden="true"></span><span class="sr-only">Close</span></button></div>';
                    $messageBlock.append(message);
                }

                // finally, re-enable button
                $this.inboxenSpinnerToggle();
            }
        });
    });
})(jQuery);
