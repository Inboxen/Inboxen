/*
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

// cleans email body of any JS events that have been accidently attached there
$(document).ready(function() {
    $("#email-body").off();
});
