# Changelog

## Releases

### Deploy for 2019-11-07

* Remove Watson completely and remove unused table (#412)
* Reset inbox flags when deleting emails (#391)
* Remove sed commands from update-py-requirements Make rule

### Deploy for 2019-10-18

* Restore `update_last_login signal` in preparation for future work (#444)
* Prevent attachments from over-expanding (#458)
* Include source maps for JS and CSS assets (#462)
* Remove redundant lambda functions
* Move add inbox button (#467)
* Simplify `find_bodies` code (#465)
* Implement new search view (#412)

### Deploy for 2019-08-06

* Remove WebAssets, we now use GruntJS to build static assets (#447)
* Switch from ruby-sass to dart-sass (#399)
* Fix issue where a single admin would cause a configuration error (#455)

### Deploy for 2019-06-09

* Fix error in the way the password change view redirects (#441)

### Deploy for 2019-06-04

* Rate limit single email download (#433)
* Improve cleaning of HTML parts to improve how they are displayed (#404)
* Fix attachment download (#437)

### Deploy for 2019-05-24

* Update to Django 2.2 (#367)
* Add feature to download a single email (#176)
* Reduce pagination size from 100 to 25. This is still more than a screen full. (#423)
* Make console commands for interacting with Salmon nicer (#216)
* Set Inbox flags to their default state when disowning (#335)
* Add feature to download backup tokens (#332)
* Remove old dependencies required for Python 2.7 and Django 1.11

### Deploy for 2019-05-01

* Fix liberation bug due to user having a prefered domain (#418)
* Add migrations required by latest release of django-mptt
* Update versioneer config to display git tags correctly

### Deploy for 2019-03-04

* Remove mock dependency (#414)
* Add new search index columns in preparation for removing django-watson (#412)

### Deploy for 2019-02-24

* Django security release

### Deploy for 2019-01-22

* Prevent Salmon from emailing errors to admins, spamming their inbox (#410)

### Deploy for 2019-01-10

* Completely removed all traces of django-bitfield (#358)
* Make Inboxen a proper Python package (#163)
* Add a check for Domains and a console command to allow creating domains (#393)
* Fix issue with exporting broken emails (#370)
* Allow users to delete their inboxes (#373)

### Deploy for 2018-10-29

* HOTFIX ``ADMINS`` should be a list, not a generator (#385)

### Deploy for 2018-06-12

* Change code to use new boolfields - requires downtime (#325)
* Allow users to auto-delete emails after 30 days (#83)
* Implement a quota system to avoid users eating all of our disk space (#359)
  * This system is entirely optional and not enabled by default

### Deploy for 2018-05-22

* Add boolean fields to replace bitfields in various models (#325)
* Make sure cache keys generated for ratelimiting are URL-safe (#354)

### Deploy for 2018-05-11

* Rate limit inbox creation and remove inbox requests feature (#350)
* Proper search (#45)
  * Pagination for search results
  * Slimmer indexing, which should also make for faster searching

### Deploy for 2018-04-14

* Proper Python 3 support (#261)
* Upgrade to Celery 4 (#222)
* Do lint checks as part of normal testing
* Add a copy button to each inbox (#100)
* Rate limit user registration (#342)
* Change "X big units, Y small units" times to just "X big units" (#337)
* Fix button column width on home view (#338)
* Fix responsiveness of stats charts (#341)
  * This will also mean that the stats page will have `'unsafe-inline'` on the stats page

### Deploy for 2018-03-23

* Fix username change form to actually change the username (#327)

### Deploy for 2018-03-15

* Tests for OTP views (#283)
* Buttons should give some visual feedback that they're doing something (#279)
* Initial JS tests (#303)
* Move from django-sudo to django-elevate (#282)
* Reduce static asset sizes
  * Use UglifyJS to mangle our JS reducing each of our JS bundles by about 50KB
  * Only import the parts of Bootstrap that we actually use, reducing our CSS bundle by about 40KB
* Add favicons for various devices (#181)

### Deploy for 2018-02-18

* Improve keyboard accessibility on home and inbox pages (#278)
* Add work-around for Django-Two-Factor-Auth bug in LoginView (#292)
* Set X-XSS-Protection to something other than its dangerous default (#297)
* Set HSTS headers in Django - this makes HSTS no longer optional (#298)
* Test security features (#298)
* Used Sixer to make source code compatible with Python 3
  * This is just a first step ot make Inboxen work on Python 3
* Use labels on admin lists for better readability (#263)
* Change text on error pages to be slightly more verbose (#302)
* Change referrer policy on email view to same-origin (#307)
* Use a more secure method to produce the random part of inboxes (#312)
* Cleaned up our use of datetime to make sure we're always using timezone away
  datetime objects
* Removed single delete button from inbox view (#76)
  * Those buttons are too easy to hit accidentally for an not-undoable action
    like deleting an email

### Deploy for 2018-01-18

* Hotfix: Fix misconfiguration of CSRF

### Deploy for 2018-01-16

* Prevent storing NULL in char and text fields (#274)
* Update to the latest release of Salmon
* Allow HTML headings in HelpPage bodies
* Make sure user creation and username change forms use the same validation (#281)
* Handle attachment name overflow properly (#273)
* Update log config to include rate limit
* Use system fonts to avoid issues with bad substitutions of named fonts (#294)

### Deploy for 2017-12-04

* Fix issue with header names not being stored in the correct format (#275)

### Deploy for 2017-12-01

* Update stats task
  * Display a running total of emails processed on stats page
  * Remove standard deviation stat, it didn't actually mean anything for our dataset
  * Store join date of oldest user in stats
  * Calculate disowned inboxes
  * Calculate `new` & `with_inboxes` via aggregate
* Update to the latest Salmon (#233)
* Properly remove Wagtail as a dependency (#254)
* Pin Python dependencies with `pip-tools` (#251)
* Increase default Inbox length (#226)
* Make sure we have valid HTML when displaying emails (#269)

### Deploy for 2017-11-13

* New admin! (#254)
  * Remove Wagtail admin
  * User-facing part of CMS is complete
  * Admin-facing part of CMS is a bit bare-bones

### Deploy for 2017-09-24

* Cycle session key to help protect against session hijacking on long lived sessions (#187)
* Update JQuery to 3.0 (#183)
* Update ChartJS to a newer version (#184)
* Update Font Awesome to 4.7.x (#185)
* Update to Django 1.11 (#165)
  * Upgrade to Wagtail 1.11
  * Fix incorrect `select_related` use
  * Removed `django-session-csrf`as it is no longer needed for Django 1.11
* Replace Javascript used to collapse navigation on smaller screens with a pure CSS solution (#241)
* Fix issue with HTML parsing around `<meta>`, sometimes it doesn't have the attributes we want

### Deploy for 2017-08-19

* Fix some corner cases in `inboxen.utils.emails.find_bodies` (#243)

### Deploy for 2017-08-16

* Wrap long lines in plain text emails (#227)
* Change how MIME parts and headers are fetched to be more generic (#109)
* Search and email view now use the same function when walking the MIME tree (#109)

### Deploy for 2017-08-05

* Pass attachment name to template for email view (#229)
* Implement a styleguide
* Don't email admins every time there's an issue with HTML emails (#235)
* Remove last vestiges of django-extensions' UUID field (#230)
* Fix `FutureWarning` being raised by LXML (#232)
* Fix translations in template tags not being lazy (#239)

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
