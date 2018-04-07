/*!
 * Copyright (c) 2018 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

describe("The Spinner Toggle plugin", function() {
    it("should be available as a jQuery plugin", function() {
        expect(jQuery.fn.inboxenSpinnerToggle).toBeDefined();
    });

    it("should be available on selector objects", function() {
        expect($("html").inboxenSpinnerToggle).toBe(jQuery.fn.inboxenSpinnerToggle);
    });

    describe("when called on buttons", function() {
        beforeEach(function() {
            this.html = $("<button><span class='fa fa-eye'></span>Click!</button>");
        });

        it("should set clicked on the button's data", function() {
            expect(this.html.data("clicked")).toBeUndefined();

            this.html.inboxenSpinnerToggle();
            expect(this.html.data("clicked")).toBe("yes");

            this.html.inboxenSpinnerToggle();
            expect(this.html.data("clicked")).toBe("no");
        });

        it("should set and unset the disabled property", function() {
            expect(this.html.prop("disabled")).toBe(false);

            this.html.inboxenSpinnerToggle();
            expect(this.html.prop("disabled")).toBe(true);

            this.html.inboxenSpinnerToggle();
            expect(this.html.prop("disabled")).toBe(false);
        });

        it("should add and remove the disabled class", function() {
            this.html.inboxenSpinnerToggle();
            expect(this.html.attr("class")).toBe("disabled");

            this.html.inboxenSpinnerToggle();
            expect(this.html.attr("class")).toBe("");
        });

        it("should add and remove the spinner class on the child span", function() {
            this.html.inboxenSpinnerToggle();
            expect(this.html.children("span").attr("class")).toBe("fa fa-eye fa-spinner fa-spin");

            this.html.inboxenSpinnerToggle();
            expect(this.html.children("span").attr("class")).toBe("fa fa-eye");
        });
    });

    describe("when called on forms", function() {
        beforeEach(function() {
            this.html = $("<form><button>Submit</button><a class='btn'>Cancel</a></form>");
        });

        it("should set clicked on the button's data", function() {
            expect(this.html.data("clicked")).toBeUndefined();

            this.html.inboxenSpinnerToggle();
            expect(this.html.data("clicked")).toBe("yes");

            this.html.inboxenSpinnerToggle();
            // forms don't get toggled back as they are reloaded
            expect(this.html.data("clicked")).toBe("yes");
        });

        it("should set the disabled property on the button", function() {
            expect(this.html.find("button").prop("disabled")).toBe(false);

            this.html.inboxenSpinnerToggle();
            expect(this.html.find("button").prop("disabled")).toBe(true);

            this.html.inboxenSpinnerToggle();
            // forms don't get toggled back as they are reloaded
            expect(this.html.find("button").prop("disabled")).toBe(true);
        });

        it("should set the disabled class on the cancel anchor button", function() {
            expect(this.html.find("a.btn").attr("class")).toBe("btn");

            this.html.inboxenSpinnerToggle();
            expect(this.html.find("a.btn").attr("class")).toBe("btn disabled");

            this.html.inboxenSpinnerToggle();
            // forms don't get toggled back as they are reloaded
            expect(this.html.find("a.btn").attr("class")).toBe("btn disabled");
        });
    });
});
