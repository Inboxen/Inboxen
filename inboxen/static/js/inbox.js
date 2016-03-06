/*!
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

$(document).ready(function() {
    var important_label = '<span class="label label-danger" title="Message has been marked as important">Important</span>';

    function ToggleImportant($row) {
        if ($row.find("span.label-danger").length === 0) {
           $row.find("div.email-flags").append(important_label);
        } else {
            $row.find("span.label-danger").remove();
        }
    }

    function MarkImportant($row) {
        if ($row.find("span.label-danger").length === 0) {
           $row.find("div.email-flags").append(important_label);
        }
    }

    function UnmarkImportant($row) {
        $row.find("span.label-danger").remove();
    }

    function DeleteRow($row) {
        $row.remove();
    }

    $("#email-list button[type=submit]").click(function(event) {
        event.preventDefault();

        var $this = $(this);
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
                    if (button.name === "important-single") {
                        ToggleImportant($row);
                        return;
                    } else if (button.name === "delete-single") {
                        DeleteRow($row);
                        return;
                    }

                    var fn;
                    if (button.name === "important") {
                        fn = MarkImportant;
                    } else if (button.name === "unimportant") {
                        fn = UnmarkImportant;
                    } else if (button.name === "delete") {
                        fn = DeleteRow;
                    } else {
                        // return early, I don't know what button was pressed
                        return;
                    }

                    $.each(form_data, function(index, value) {
                        if (value.value === "email") {
                            fn($("#email-" + value.name));
                        }
                    });
                } else {
                    var $messageBlock = $("#alertmessages");
                    var message = '<div class="alert alert-warning" role="alert">Something went wrong!<button type="button" class="close" data-dismiss="alert"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span><span class="sr-only">Close</span></button></div>';
                    $messageBlock.append(message);
                }
            }
        });
    });
});
