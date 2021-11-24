/*!
 * Copyright (c) 2015-2016 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/main/LICENSE)
 */

(function($){
    'use strict';

    $(".inbox-options button[name=pin-inbox]").click(function(event) {
        event.preventDefault();

        var $this = $(this);
        if ($this.data("clicked") === "yes") {
            return false;
        }

        $this.inboxenSpinnerToggle();

        var button = {"name": $this.attr("name"), "value": $this.attr("value")};
        var $form = $this.parent("form");
        var form_data = $form.serializeArray();
        form_data.push(button);

        $.ajax({
            type: "POST",
            url: $this.parent("form").data("url"),
            data: form_data,
            complete: function(xhr, statusText) {
                if (xhr.status === 204) {
                    var $row = $("#" + $form.data("inbox-selector"));
                    if ($row.find("span.label-warning").length === 0) {
                        window.snippet("pinned-flag").then(function(pinned) {
                            $row.find("div.inbox-flags").append(pinned);
                        });
                    } else {
                        $row.find("span.label-warning").remove();
                    }
                } else {
                    var $messageBlock = $("#alertmessages");
                    var $msg;
                    window.snippet("generic-error").then(function(message) {
                        $msg = message;
                        $messageBlock.append($msg);
                        return window.snippet("button");
                    }).then(function(button) {
                        $msg.append(button);
                    });
                }

                // finally, re-enable button
                $this.inboxenSpinnerToggle();
            }
        });
    });
})(jQuery);

(function($){
    'use strict';

    function initForm($form, completeCallback) {
        $form.submit(function(event) {
            event.preventDefault();
            var $this;

            $this = $(this);
            $this.$form = $form;

            if ($this.data("clicked") === "yes") {
                return false;
            }

            $this.inboxenSpinnerToggle();

            $.ajax({
                type: "POST",
                url: $this.attr('action'),
                data: $this.serializeArray(),
                complete: completeCallback.bind(null, $this)
            });
        });
    }

    function homeFormComplete($this, xhr, statusText) {
        var description, inboxSelector, is_disabled, is_pinned, $row;

        inboxSelector = $this.$form.data("inbox-selector");
        $row = $("#" + inboxSelector + " + .row");
        description = $this.find("#id_description").val();
        is_disabled = $this.find("#id_disable_inbox").prop("checked");
        is_pinned = $this.find("#id_pinned").prop("checked");

        if (xhr.status === 204) {
            var $inbox_row = $("#" + inboxSelector);
            var $description_cell = $inbox_row.find(".inbox-description");

            $description_cell.text(description);

            if (is_disabled && !$inbox_row.hasClass("inbox-disabled")) {
                $inbox_row.addClass("inbox-disabled");
                $inbox_row.find(".inbox-flags").empty();
                window.snippet("disabled-flag").then(function(flag) {
                    $inbox_row.find(".inbox-flags").append(flag);
                });
            } else if (!is_disabled && $inbox_row.hasClass("inbox-disabled")) {
                $inbox_row.removeClass("inbox-disabled");
                $inbox_row.find(".inbox-flags").empty();
            } else if (is_pinned && !is_disabled && $inbox_row.find("span.label-warning").length === 0) {
                window.snippet("pinned-flag").then(function(flag) {
                    $inbox_row.find(".inbox-flags").append(flag);
                });
            } else if (!is_pinned && !is_disabled) {
                $inbox_row.find("span.label-warning").remove();
            }

            $row.remove();
        } else if (xhr.status === 200) {
            $this.$form.removeData().html(xhr.responseText);
            initForm($this.$form, homeFormComplete);
            $row.find("a").click(function() {
                $row.remove();
            });
        } else {
            window.snippet("generic-error").then(function(error) {
                $this.$form.replaceWith(error);
                console.log("Form for " + inboxSelector + " failed to POST (" + xhr.status + ")");
            });
        }
    }

    function inboxFormComplete($this, xhr, statusText) {
        if (xhr.status === 204) {
            $this.$form.parents(".inbox-edit-form-row").remove();
        } else {
            if (xhr.status === 200) {
                $this.$form.removeData().html(xhr.responseText);
                initForm($this.$form, inboxFormComplete);
                $this.$form.parents(".inbox-edit-form-row").find("a").click(function($this) {
                    $this.$form.parents(".inbox-edit-form-row").remove();
                }.bind(null, $this));
            } else {
                window.snippet("generic-error").then(function(error) {
                    $this.$form.replaceWith(error);
                    console.log("Form failed to POST (" + xhr.status + ")");
                });
            }
        }
    }

    function addInboxComplete($this, xhr, statusText) {
        if (xhr.status === 204) {
            // hacky, but this will have to do for now
            // in fact very hacky as it will lock up the window!
            document.location.reload(true);
        } else {
            if (xhr.status === 200) {
                $this.$form.removeData().html(xhr.responseText);
                initForm($this.$form, addInboxComplete);
                $("#inbox-add-form").find("a").click(function() {
                    $("#inbox-add-form").remove();
                });
            } else {
                window.snippet("generic-error").then(function(error) {
                    $this.$form.replaceWith(error);
                    console.log("Form failed to POST (" + xhr.status + ")");
                });
            }
        }
    }

    // adds event listeners for inline forms to be popped in
    $("#inbox-list .inbox-options .inbox-options-btn").click(function() {
        // option buttons on inbox list
        var $this = $(this);
        var $row = $this.parents("div.row:has(.inbox-name)");
        var formURL = "/forms/inbox/edit/" + $row.attr("id") + "/";

        if (!$row.next().hasClass("inbox-edit-form-row")) {
            if ($this.data("clicked") === "yes") {
                return false;
            }

            $this.inboxenSpinnerToggle();

            $.get(formURL, function(data) {
                // double check
                if (!$row.next().hasClass("inbox-edit-form-row")) {
                    $row.after("<div class=\"inbox-edit-form-row row\"><div class=\"col-xs-12\">" + data + "</div></div>");
                    initForm($row.next().find("form"), homeFormComplete);
                    $row.next().find("a").click(function() {
                        $row.next().remove();
                    });
                }

                // finally, re-enable button
                $this.inboxenSpinnerToggle();
            });
        } else if ($row.next().hasClass("inbox-edit-form-row")) {
            $row.next().remove();
        }
        return false;
    });

    $("#email-list .inbox-edit").click(function() {
        // option button on inbox page
        var $this = $(this);
        var $table = $(".honeydew");
        var formURL = "/forms/inbox/edit/" + $this.data("inbox-id") + "/";

        if (!$table.children(":first").hasClass("inbox-edit-form-row")) {
            if ($this.data("clicked") === "yes") {
                return false;
            }

            $this.inboxenSpinnerToggle();

            $.get(formURL, function(data) {
                // double check
                if (!$table.children(":first").hasClass("inbox-edit-form-row")) {
                    $table.prepend("<div class=\"inbox-edit-form-row row\"><div class=\"col-xs-12\">" + data + "</div></div>");
                    initForm($table.children(":first").find("form"), inboxFormComplete);
                    $table.children(":first").find("a").click(function() {
                        $table.children(":first").remove();
                    });
                }

                // finally, re-enable button
                $this.inboxenSpinnerToggle();
            });
        } else if ($table.children(":first").hasClass("inbox-edit-form-row")) {
            $table.children(":first").remove();
        }
        return false;
    });

    $("#add-inbox").click(function() {
        var $this = $(this);

        if ($this.data("clicked") === "yes" || $("#inbox-add-form").length !== 0) {
            return false;
        }

        $this.inboxenSpinnerToggle();

        $.get($this.data("form-url"), function(data) {
            var $addForm;

            $addForm = $("<div id=\"inbox-add-form\" class=\"row\"><div class=\"col-xs-12 col-sm-6 col-sm-offset-3 col-md-4 col-md-offset-4 col-lg-4 col-lg-offset-4\"><div class=\"panel panel-default\"><div class=\"panel-body\">" + data + "</div></div></div></div>");
            $this.hide();
            $this.after($addForm);
            initForm($addForm.find("form"), addInboxComplete);
            $addForm.find("a").click(function() {
                $addForm.remove();
                $this.show();
            });

            // finally, re-enable button
            $this.inboxenSpinnerToggle();
        });
        return false;
    });
})(jQuery);
