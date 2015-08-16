/*
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */
$(document).ready(function() {
    // collapsing nav
    // we do this here so that the nav still works for those without JS
    $("#navbar-button-1").removeClass("hidden");
    $("#navbar-collapse-1").addClass("collapse navbar-collapse");

    // alert buttons
    var button = '<button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">{% trans "Close" %}</span></button>';
    $("div[role=alert]").each(function() {
        $(this).append(button);
    });
});
