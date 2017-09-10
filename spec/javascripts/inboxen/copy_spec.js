/*!
 * Copyright (c) 2018 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

describe("The Inbox Copy Button plugin", function() {
    it("should be available as a jQuery plugin", function() {
        expect(jQuery.fn.inboxenInboxCopyBtn).toBeDefined();
    });

    it("should be available on selector objects", function() {
        expect($("html").inboxenInboxCopyBtn).toBe(jQuery.fn.inboxenInboxCopyBtn);
    });

    describe("when called", function() {
        beforeEach(function() {
            this.html = $(`
            <div id="fixture">
                <div class="parent-thing">
                    <div>notanemail@example.com</div>
                    <div class="child-thing">other@example.com</div>
                </div>
                <div id="inbox-list" data-inbox-name=".inbox-name a"
                data-button-container=".inbox-options > form"
                data-children=".row" data-button-classes="close"
                data-button-title="Clipboard">
                    <div class="row">
                        <div class="inbox-name"><a>bob</a></div>
                        <div class="inbox-options"><form></form></div>
                        <div><form></form></div>
                    </div>
                    <div class="row">
                        <div class="inbox-name"><a>thing@example.com</a></div>
                        <div class="inbox-options"><form><button>test</button></form></div>
                        <div><form></form></div>
                    </div>
                </div>
                <div id="email-list" data-inbox-name=".parent-thing .child-thing"
                data-button-container=".btn-group"
                data-button-classes="btn btn-default"
                data-button-text="Clipboard">
                    <div class="btn-group"><button>Button!</button></div>
                    <div class="row"></div>
                </div>
            </div>
            `);
            $("html").append(this.html);
        });

        afterEach(function() {
            $("#fixture").remove();
        });

        describe("on #inbox-list", function() {
            beforeEach(function() {
                this.html.find("#inbox-list").inboxenInboxCopyBtn();
            });

            it("should add a new button", function() {
                var button = this.html.find(".inbox-options form button.close");
                expect(button.length).toBe(1);
                expect(this.html.find("span").length).toBe(2);
                expect(this.html.find("span").parent().toArray()).toEqual(button.toArray());
            });

            it("should listen to the click event", function() {
                var button = this.html.find(".inbox-options form button.close");
                spyOn(document, "execCommand");

                button.click();
                expect(document.execCommand).toHaveBeenCalledTimes(1);
                expect(document.execCommand).toHaveBeenCalledWith("copy");
            });

            it("should select the correct text", function() {
                var selection, range;
                var button = this.html.find(".inbox-options form button.close");
                window._inboxenSelectedText = "";

                spyOn(document, "execCommand").and.callFake(function() {
                    var selection = window.getSelection();
                    window._inboxenSelectedText = selection.toString();
                });

                // select the wrong text first
                selection = window.getSelection();
                range = document.createRange();
                range.selectNodeContents(this.html.find(".inbox-name:first a")[0]);
                selection.removeAllRanges();
                selection.addRange(range);

                button.click();
                expect(window._inboxenSelectedText).toBe("thing@example.com");
            });
        });

        describe("on #email-list", function() {
            beforeEach(function() {
                this.html.find("#email-list").inboxenInboxCopyBtn();
            });

            it("should add a new button", function() {
                var button = this.html.find(".btn-group button.btn");
                expect(button.length).toBe(1);
                expect(this.html.find("span").length).toBe(2);
                expect(this.html.find("span").parent().toArray()).toEqual(button.toArray());
            });

            it("should listen to the click event", function() {
                var button = this.html.find(".btn-group button.btn");
                spyOn(document, "execCommand");

                button.click();
                expect(document.execCommand).toHaveBeenCalledTimes(1);
                expect(document.execCommand).toHaveBeenCalledWith("copy");
            });

            it("should select the correct text", function() {
                var selection, range;
                var button = this.html.find("button.btn");
                window._inboxenSelectedText = "";

                spyOn(document, "execCommand").and.callFake(function() {
                    var selection = window.getSelection();
                    window._inboxenSelectedText = selection.toString();
                });

                // select the wrong text first
                selection = window.getSelection();
                range = document.createRange();
                range.selectNodeContents(this.html.find(".inbox-name:first a")[0]);
                selection.removeAllRanges();
                selection.addRange(range);

                button.click();
                expect(window._inboxenSelectedText).toBe("other@example.com");
            });
        });

        describe("on an element that does not have the correct data attributes", function(){
            it("should do nothing", function() {
                var buttons, buttonCount;
                buttonCount = this.html.find("button").length;
                this.html.inboxenInboxCopyBtn();

                buttons = this.html.find("button");
                // no buttons should have been added
                expect(buttons.length).toBe(buttonCount);
            });
        });

        describe("on a browser that doesn't support 'copy'", function() {
            it("should do nothing", function() {
                var buttons, buttonCount;
                buttonCount = this.html.find("button").length;

                spyOn(document, "queryCommandSupported").and.returnValue(false);
                this.html.find("#inbox-list").inboxenInboxCopyBtn();

                buttons = this.html.find("button");
                // no buttons should have been added
                expect(buttons.length).toBe(buttonCount);
            });
        });
    });
});
