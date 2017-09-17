/*!
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

(function($) {
    'use strict';
    // alert buttons
    var button = '<button type="button" class="close" data-dismiss="alert"><span class="fa fa-times" aria-hidden="true"></span><span class="sr-only">Close</span></button>';
    $("div[role=alert]").each(function() {
        $(this).append(button);
    });
})(jQuery);
