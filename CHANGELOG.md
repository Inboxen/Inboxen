# Changelog

## Pending

* Pass attachment name to template for email view (#229)
* Implement a styleguide
* Don't email admins every time there's an issue with HTML emails (#235)

## Releases

### Deploy for 2017-06-17

* Display the text version of the 2FA secret code at the same time as the QR code (#190)
* Change error message feeder command gives when inbox does not exit
* Fix non-ASCII filename handling in attachment download (#206)
* Drop Sqlite support (#214)
* Remove "view" button from attachments (#202)
* Stop proxying non-HTTP URIs (e.g. mailto:) (#211)
* Tests are now run with the test settings module by default

### Deploy for 2017-05-20

* Fix ratelimit warnings in tests (#197)
* Disable certain actions in the admin interface (e.g. disable deleting Domains (#193))
* Fix 500 error on questions form error (#204)
* Add missing copyright headers (#194)

### Deploy for 2017-04-14

* Added Wagtail CMS (#162)
* Added periodic task to clear stale sessions (#186)
* Refactor liberation utils (#189)

### Deploy for 2017-02-25

* Order disabled inboxes to the end of the inbox list (#177)
* Add target=\_blank back to email links. Reverts #131 (#174)
* Update Django-twofactor-auth usage to reflect API changes (#178)

### Deploy for 2016-10-16

* Detect bounced emails sent to support@ (#172)
* Fix CSP headers for Django 1.9 admin pages (#171)

### Deploy for 2016-10-02

* Emails to support@ will now be routed to admins correctly (#169)
* "Super user" mode has been implemented (#164)
* More errors to be caught when CSS transformations fail (#159)
* Fixes for CSP and IE Edge (#167)
* Use the latest Django-CSP (#158)

### Deploy for 2016-08-30

* Apply hotfix-20160830

### Deploy for 2016-07-10

* Fix bug where JS was not applied to forms after an error (#156)
* Fix bug in search where a variable wasn't properly initialised (#157)
* Add a pin inbox button to user home page (#147)

### Deploy for 2016-06-13

* Tickets app is more mobile friendly (#127)
* Don't rely on Content-Type containing a charset in HTML bodies (#155)
* Add icons to buttons (#152)
* Remove hover styles from inline forms (#154)
* Inline add inbox form - add an inbox from anywhere! (#49)
* Make subject/description boxes of honeydew sections clickable areas (#149)
* Remove CBV cruft (#153)
* Improved stats/charts (#148)
* Replace non-freeish Glyphicons with Font Awesome (#143)

### Deploy for 2016-05-08

* Bypass Premailer if HTML part has no body (#151)
* Fix next/previous page buttons

### Deploy for 2016-04-24

* Pin inboxes #129
* Use `django.contrib.humanize` #139
* List total possible inboxes on stats page #103
* Add charts to stats page #141
* Tighen up URLConf to avoid over-matching #142

### Deploy for 2016-03-29

* Improve admin site #135 #136
* Fix logging, specifically notying admins when something goes wrong #138
* Prompt users to create backup devices when they enable 2FA #72
* A minor collection of styling bug fixes

### Deploy for 2016-03-21

* Remove separate admin settings #134
* Improve home view CSS on mobile #133
* Fix alignment issues on small screens on inbox view #132

### Deploy for 2016-03-20

* Fix `window.opener` issue #131
* Edit inbox from email list view #84
* Enable Django's security middleware #123
* Switch to Bootstrap's grid system for inbox and email lists #71
* Switch to whitelisting HTML tags and attributes #121
* Django 1.9 #124
* Use AppConfig #117
* Test coverage for management commands #128

### Deploy for 2015-12-24

* Improve the UI for tickets #119
* Rolling session #104
* Simplified queryset building in InboxView
* Unbundle front-end libraries #120
* Minifiers now respect copyright headers in JS and CSS #120 #118
* Turn off CSP report-only mode #116
* Fix logging #87

### Deploy for 2015-12-13

* Fixed error when attachment not found #110
* Blog posts now have a slug, old posts use their PK as their slug #113
* New placeholder image for HTML emails #115
* Users now get a message when they log out #112

* Revert brand link behaviour
* Ensure all body parts are escaped properly

### Deploy for 2015-12-06

* Major upgrade to Django 1.8
* Go back to storing liberation data on filesystem
* Reorganise apps to be more logical - no more "website" app
* Use version 3 of the Celery API
* View more than one body in an email under certain rules
* Updated front page - now the default home page even for logged in users
* A bunch of other changes that I've forgotten about

### Deploy for 2015-09-17

* Use session based CSRF tokens #80
* Change the way attachments are displayed #91
* Remove "import" script, it was mostly useless
* Change search form to not violate our CSP settings #86
* Links from blog and emails now open a new tab #92

### Deploy for 2015-09-06

* CSP is now enabled, only in reporting mode for now #81
* Added copyright headers to assets, webassets strips them out #79
* Block browers from sending Referer headers #62
* Remove inline JS #82
* Don't use the latest version of d2fa, they've dropped Django 1.6 support
* Blacklist buggy version of django-model-utils #78
* Remove footer from maintenance page, those links won't work if the site is down

### Deploy for 2015-06-30

* Fix ordering issue from last deploy

### Deploy for 2015-06-29

* Replace "created" with "last activity"
* Display Inbox link on Unified view
* Skip fewer unit tests due to old bugs
* Stop assets randomly failing during tests
* Clean up search task a bit - see 5c7cb64145cf2a411a89ae0caad4430f11336ad0
* Fix possible data leak - see f705ad373c2f99c976fd153b92d3aac305632442

### Deploy for 2015-06-18

* Webassets and such!

### Deployments before 2015-06-18

Sorry, we didn't keep a changelog before this date
