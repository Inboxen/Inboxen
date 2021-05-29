/*!
 * Copyright (c) 2018 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/main/LICENSE)
 */

describe("The Alert plugin", function() {
    it("should be available as a jQuery plugin", function() {
        expect(jQuery.fn.alert).toBeDefined();
    });

    it("should be available on selector objects", function() {
        expect($("html").alert).toBe(jQuery.fn.alert);
    });
});
