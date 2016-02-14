# -*- coding: utf-8 -*-
##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##


BODY = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<style type="text/css">
p {color: #ffffff;background:transparent url(<a href="http://cdn-images.mailchimp.com/awesomebar-sprite.png">http://cdn-images.mailchimp.com/awesomebar-sprite.png</a>) 0 -200px;}
</style>
<script><!-- console.log("I'm a bad email") --></script>
</head>
<body>
<p>Hello! This is a test of <img src="http://example.com/coolface.jpg"></p>
<p>&nbsp;</p>
<p>£££</p><p><a href="http://example.com/?q=thing">link</a></p>
<p><a>Ha!</a><img width=10 height=10></p>
<p onClick="alert('Idiot!')">Click me!</p>
</body>
</html>
"""


METALESS_BODY = """<html>
<head>
<style type="text/css">
p {color: #ffffff;background:transparent url(<a href="http://cdn-images.mailchimp.com/awesomebar-sprite.png">http://cdn-images.mailchimp.com/awesomebar-sprite.png</a>) 0 -200px;}
</style>
</head>
<body>
<p>Hello! This is a test of <img src="http://example.com/coolface.jpg"></p>
<p>&nbsp;</p>
<p>$$$</p><p><a href="http://example.com/?q=thing">link</a></p>
<p><a>Ha!</a><img width=10 height=10></p>
</body>
</html>
"""


# example email that was causing issue #47
EXAMPLE_PREMAILER_BROKEN_CSS = """Return-Path: <bounces@server8839.e-activist.com>
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed; s=key1;
 d=server8839.e-activist.com;
 h=Date:From:To:Message-ID:Subject:MIME-Version:Content-Type;
 bh=1jrlURfYD1LWHl2z3K44WJaUuaq04WhJz2dFSEV0NiI=;
 b=Bi9w2cPlpPuXsWCHX3rgIQfm/fZnk7yHsbl6yEZIETTYDDGc5lJc5mBoAQRZ4CiOsiw2XvP6MPvi
 ysDFXeKVq7TcgaD53BPDsvW3m/ECP5iwvxowiisCo8jA++TVCcTThCoXSIQqMQz2dfb5YfY/X7/D
 /56XO4Ye7msiPGlUZ1c=
Date: Fri, 20 Nov 2015 07:02:04 -0500 (EST)
From: Ruth Coustick-Deal -ORG <ruth@openrightsgroup.org>
To: example@example.com
Message-ID: <2004200797.99171901448020924829.JavaMail.root@server9849>
Subject: ORG News: Spotlight on the IPB
MIME-Version: 1.0
Content-Type: multipart/related;  boundary="----=_Part_29748710_445134290.1448020924829"
campaignerId: 5180535
broadcastSendId: 95540;
X-Auto-Response-Suppress: OOF


------=_Part_29748710_445134290.1448020924829
Content-Type: multipart/alternative;  boundary="----=_Part_29748709_1445524343.1448020924829"


------=_Part_29748709_1445524343.1448020924829
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: quoted-printable

Dear Matt Molyneaux,

Here's your newsletter from the frontline of digital
rights: defending and promoting citizens' rights in the digital age.
This update and previous versions are now available from our website: https=
://www.openrightsgroup.org/support-org/


PARIS ATTACK
We'd planned to send an email about the Investigatory Powers Bill earlier t=
his
week. After the horrific attacks on Friday, it just didn't feel right. We d=
idn't
really want to campaign or comment on surveillance in the UK.

But over the last couple of days, we've heard politicians call for the IPB =
to be
fast tracked through Parliament and we=E2=80=99ve been asked what we think =
of this. We
understand that people are rightly concerned about surveillance powers in t=
he
UK, but this is not the time to rush through legislation.

The Paris attacks were not just brutal murders but an assault on our freedo=
m and
liberty. We cannot let terrorists undermine our fundamental values through =
a
knee-jerk reaction to these terrible events.

Interestingly, we appear to be in agreement with the Home Secretary, Theres=
a May
who said this week:

'The draft Investigatory Powers Bill is a significant measure that we expec=
t to
stand the test of time. We do not want future Governments to have to change
investigatory powers legislation constantly, so it is important that we get=
 it
right. It is therefore important that the Bill receives proper scrutiny and=
 that
it has support across the House, given the nature of it.'

So we're sending this email because it's important that we get on and scrut=
inise
this Bill and speak out against that the parts that undermine our fundament=
al
rights. As ever, we are going to need your help to do this.


WHAT'S THE STATUS OF THE IPB?
Although some politicians, like Lord Carlisle, called for the Investigatory
Powers Bill to be fast-tracked this week, it is currently scheduled to stil=
l
follow the proper process.

This means that there is an opportunity for the a full discussion about
surveillance, the one we've been calling for these past years.

What happens next is that a committee of MPs and Lords will scrutinise the =
Bill.
ORG will provide evidence to that Committee, and we=E2=80=99ll help you do =
so too.

When that stage is over, they will report in the new year with suggestions =
for
changes to the Bill.

We then expect MPs to vote on the final version in spring. This is why it i=
s
important to start talking to them now
; so they are aware of the concerns that their constituents have about the
Bill, and to get them to pay attention to this huge piece of surveillance l=
aw.
[https://www.openrightsgroup.org/campaigns/investigatory-powers-bill-email-=
your-mp]=20

TAKE ACTION TODAY!

The people scrutinising the law are not working in a bubble. They listen to
colleagues and their leadership. They listen to the voices around them and =
how
the public is thinking.

You can help influence them by asking your MP to talk to members of those
committees. We all need to start talking to MPs now to get them thinking ab=
out
the IPB.

You can tell your MP why they should be concerned about the Bill here:

[https://www.openrightsgroup.org/campaigns/investigatory-powers-bill-email-=
your-mp]

This is only the start of the campaign. We've already been talking to
politicians and the media about the IPB. We met with Andy Burnham, Shadow H=
ome
Secretary and other Labour politicians this week to discuss our concerns.
In the coming months, we'll be working together with you to rip out the
dangerous parts of this Bill. We can do this!

WHAT'S IN THE BILL?
The Investigatory Powers Bill is a new law on surveillance that was present=
ed to
parliament in November 2015. Unlike the Communications Data Bill, the IPB c=
overs
both the police and security services=E2=80=99 powers.

Key issues in the Bill

-It clarifies the powers of security agencies to break into our laptops and
mobile phones, including powers for mass hacking. The Bill also forces inte=
rnet
companies to help in hacking their customers.

-It forces Internet Service Providers to collect and keep a record of all t=
he
websites that their customers visit.

-It does not limit the mass surveillance revealed by Edward Snowden, but in=
stead
puts those abilities into law.

This includes powers of bulk collection and analysis of data collected by
tapping Internet cables, ie. ' Tempora [https://wiki.openrightsgroup.org/wi=
ki/Tempora] '.
We=E2=80=99ll be publishing a full briefing on the Bill to help you talk to=
 your MP.OUR BIRTHDAY PARTY
ORG has worked hard over the last 10 years to ensure that everyone=E2=80=99=
s rights are
protected (You can see a whole timeline of our successes here)=20
[https://www.openrightsgroup.org/ourwork/successes/].

Now we=E2=80=99re celebrating that history with a small party in London, an=
d we=E2=80=99d love
it if you could make it to celebrate with us! RSVP:
[http://www.meetup.com/ORG-London/events/226537708/]

Date: November 27th
Time: 7.00 - 10.00pm
Location: Newspeak House
[http://maps.google.com/maps?f=3Dq&hl=3Den&q=3D133-135+Bethnal+Green+Road%2=
C+E2+7DG%2C+London%2C+gb] , 133-135 Bethnal Green Road, E2 7DG, London
Cost: =C2=A35 Hear from an excellent speaker and enjoy some birthday cake a=
t the
brand new Newspeak House in Shoreditch for our 10th anniversary!

GET INVOLVED
It=E2=80=99s our job to stand up for your rights online. If you have a mome=
nt to spare
can you help us by becoming a member of ORG [http://www.openrightsgroup.org=
/join] ?

You can find out about more ways to get involved here:
[https://www.openrightsgroup.org/get-involved]

QUICK FIRE NEWS

We'd like to welcome our latest corporate supporters, Isotoma [https://www.=
isotoma.com/] , Uno [https://www.uno.net.uk/] , Numbergroup [http://www.num=
bergroup.com/] and VPN Compare [https://www.vpncompare.co.uk/],
and thank them for supporting us in our campaigning for digital rights.=20

Our groups in Sheffield and Edinburgh have been meeting this week to discus=
s the Investigatory Powers Bill and plan local campaigns together.

ORG OUT AND ABOUT
ORG's 10th Anniversary Party
[http://www.meetup.com/ORG-London/events/226537708/]
Friday 27th November
7 PM to 10:00 PM
Newspeak House
[http://maps.google.com/maps?f=3Dq&hl=3Den&q=3D133-135+Bethnal+Green+Road%2=
C+E2+7DG%2C+London%2C+gb] , 133-135 Bethnal Green Road, E2 7DG, London

Thank you for supporting digital rights.
Best wishes,
Ruth=20


Follow us on Twitter [https://twitter.com/openrightsgroup] | Find us on Fac=
ebook [https://www.facebook.com/openrightsgroup] | Add us on Google+ [https=
://plus.google.com/116543318055985390327/posts] We need your help [https://=
www.openrightsgroup.org/volunteer] to fight for your rights and to keep the=
 web open and free. Our mailing address is: 12 Tileyard Road
London
N7 9AH This email was delivered to: moggers87@m87.co.uk; If you wish to opt=
 out
of future emails, you can do so here [https://www.openrightsgroup.org/unsub=
scribe] . | Join ORG [https://www.openrightsgroup.org/join]
------=_Part_29748709_1445524343.1448020924829
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: quoted-printable

<html>
<head>
=09<title></title>
</head>
<body><!-- Facebook sharing information tags -->
<style type=3D"text/css"><!--
=09=09=09/* Client-specific Styles */
=09=09=09#outlook a{padding:0;} /* Force Outlook to provide a "view in brow=
ser" button. */
=09=09=09body{width:100% !important;} .ReadMsgBody{width:100%;} .ExternalCl=
ass{width:100%;} /* Force Hotmail to display emails at full width */
=09=09=09body{-webkit-text-size-adjust:none;} /* Prevent Webkit platforms f=
rom changing default text sizes. */
=09=09=09
=09=09=09/* Reset Styles */g
=09=09=09body{margin:0; padding:0;}
=09=09=09img{border:0; height:auto; line-height:100%; outline:none; text-de=
coration:none;}
=09=09=09table td{border-collapse:collapse;}
=09=09=09#backgroundTable{height:100% !important; margin:0; padding:0; widt=
h:100% !important;}
=09=09=09
=09=09=09/* Template Styles */

=09=09=09/* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: COMMON PAGE ELEMENTS /\/=
\/\/\/\/\/\/\/\/\ */

=09=09=09/**
=09=09=09* @tab Page
=09=09=09* @section background color
=09=09=09* @tip Set the background color for your email. You may want to ch=
oose one that matches your company's branding.
=09=09=09* @theme page
=09=09=09*/
=09=09=09body, #backgroundTable{
=09=09=09=09/*@editable*/ background-color:#FAFAFA;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Page
=09=09=09* @section email border
=09=09=09* @tip Set the border for your email.
=09=09=09*/
=09=09=09#templateContainer{
=09=09=09=09/*@editable*/ border: 1px solid #DDDDDD;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Page
=09=09=09* @section heading 1
=09=09=09* @tip Set the styling for all first-level headings in your emails=
. These should be the largest of your headings.
=09=09=09* @style heading 1
=09=09=09*/
=09=09=09h1, .h1{
=09=09=09=09/*@editable*/ color:#202020;
=09=09=09=09display:block;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:34px;
=09=09=09=09/*@editable*/ font-weight:bold;
=09=09=09=09/*@editable*/ line-height:100%;
=09=09=09=09margin-top:0;
=09=09=09=09margin-right:0;
=09=09=09=09margin-bottom:10px;
=09=09=09=09margin-left:0;
=09=09=09=09/*@editable*/ text-align:left;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Page
=09=09=09* @section heading 2
=09=09=09* @tip Set the styling for all second-level headings in your email=
s.
=09=09=09* @style heading 2
=09=09=09*/
=09=09=09h2, .h2{
=09=09=09=09/*@editable*/ color:#202020;
=09=09=09=09display:block;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:30px;
=09=09=09=09/*@editable*/ font-weight:bold;
=09=09=09=09/*@editable*/ line-height:100%;
=09=09=09=09margin-top:0;
=09=09=09=09margin-right:0;
=09=09=09=09margin-bottom:10px;
=09=09=09=09margin-left:0;
=09=09=09=09/*@editable*/ text-align:left;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Page
=09=09=09* @section heading 3
=09=09=09* @tip Set the styling for all third-level headings in your emails=
.
=09=09=09* @style heading 3
=09=09=09*/
=09=09=09h3, .h3{
=09=09=09=09/*@editable*/ color:#202020;
=09=09=09=09display:block;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:26px;
=09=09=09=09/*@editable*/ font-weight:bold;
=09=09=09=09/*@editable*/ line-height:100%;
=09=09=09=09margin-top:0;
=09=09=09=09margin-right:0;
=09=09=09=09margin-bottom:10px;
=09=09=09=09margin-left:0;
=09=09=09=09/*@editable*/ text-align:left;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Page
=09=09=09* @section heading 4
=09=09=09* @tip Set the styling for all fourth-level headings in your email=
s. These should be the smallest of your headings.
=09=09=09* @style heading 4
=09=09=09*/
=09=09=09h4, .h4{
=09=09=09=09/*@editable*/ color:#202020;
=09=09=09=09display:block;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:22px;
=09=09=09=09/*@editable*/ font-weight:bold;
=09=09=09=09/*@editable*/ line-height:100%;
=09=09=09=09margin-top:0;
=09=09=09=09margin-right:0;
=09=09=09=09margin-bottom:10px;
=09=09=09=09margin-left:0;
=09=09=09=09/*@editable*/ text-align:left;
=09=09=09}

=09=09=09/* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: PREHEADER /\/\/\/\/\/\/\=
/\/\/\ */

=09=09=09/**
=09=09=09* @tab Header
=09=09=09* @section preheader style
=09=09=09* @tip Set the background color for your email's preheader area.
=09=09=09* @theme page
=09=09=09*/
=09=09=09#templatePreheader{
=09=09=09=09/*@editable*/ background-color:#FAFAFA;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Header
=09=09=09* @section preheader text
=09=09=09* @tip Set the styling for your email's preheader text. Choose a s=
ize and color that is easy to read.
=09=09=09*/
=09=09=09.preheaderContent div{
=09=09=09=09/*@editable*/ color:#505050;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:10px;
=09=09=09=09/*@editable*/ line-height:100%;
=09=09=09=09/*@editable*/ text-align:left;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Header
=09=09=09* @section preheader link
=09=09=09* @tip Set the styling for your email's preheader links. Choose a =
color that helps them stand out from your text.
=09=09=09*/
=09=09=09.preheaderContent div a:link, .preheaderContent div a:visited, /* =
Yahoo! Mail Override */ .preheaderContent div a .yshortcuts /* Yahoo! Mail =
Override */{
=09=09=09=09/*@editable*/ color:#336699;
=09=09=09=09/*@editable*/ font-weight:normal;
=09=09=09=09/*@editable*/ text-decoration:underline;
=09=09=09}

=09=09=09/* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: HEADER /\/\/\/\/\/\/\/\/=
\/\ */

=09=09=09/**
=09=09=09* @tab Header
=09=09=09* @section header style
=09=09=09* @tip Set the background color and border for your email's header=
 area.
=09=09=09* @theme header
=09=09=09*/
=09=09=09#templateHeader{
=09=09=09=09/*@editable*/ background-color:#FFFFFF;
=09=09=09=09/*@editable*/ border-bottom:0;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Header
=09=09=09* @section header text
=09=09=09* @tip Set the styling for your email's header text. Choose a size=
 and color that is easy to read.
=09=09=09*/
=09=09=09.headerContent{
=09=09=09=09/*@editable*/ color:#202020;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:34px;
=09=09=09=09/*@editable*/ font-weight:bold;
=09=09=09=09/*@editable*/ line-height:100%;
=09=09=09=09/*@editable*/ padding:0;
=09=09=09=09/*@editable*/ text-align:center;
=09=09=09=09/*@editable*/ vertical-align:middle;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Header
=09=09=09* @section header link
=09=09=09* @tip Set the styling for your email's header links. Choose a col=
or that helps them stand out from your text.
=09=09=09*/
=09=09=09.headerContent a:link, .headerContent a:visited, /* Yahoo! Mail Ov=
erride */ .headerContent a .yshortcuts /* Yahoo! Mail Override */{
=09=09=09=09/*@editable*/ color:#336699;
=09=09=09=09/*@editable*/ font-weight:normal;
=09=09=09=09/*@editable*/ text-decoration:underline;
=09=09=09}

=09=09=09#headerImage{
=09=09=09=09height:auto;
=09=09=09=09max-width:600px;
=09=09=09}

=09=09=09/* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: MAIN BODY /\/\/\/\/\/\/\=
/\/\/\ */

=09=09=09/**
=09=09=09* @tab Body
=09=09=09* @section body style
=09=09=09* @tip Set the background color for your email's body area.
=09=09=09*/
=09=09=09#templateContainer, .bodyContent{
=09=09=09=09/*@editable*/ background-color:#FFFFFF;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Body
=09=09=09* @section body text
=09=09=09* @tip Set the styling for your email's main content text. Choose =
a size and color that is easy to read.
=09=09=09* @theme main
=09=09=09*/
=09=09=09.bodyContent div, .bodyContent div p{
=09=09=09=09/*@editable*/ color:#505050;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:14px;
=09=09=09=09/*@editable*/ line-height:150%;
=09=09=09=09/*@editable*/ text-align:left;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Body
=09=09=09* @section body link
=09=09=09* @tip Set the styling for your email's main content links. Choose=
 a color that helps them stand out from your text.
=09=09=09*/
=09=09=09.bodyContent div a:link, .bodyContent div a:visited, /* Yahoo! Mai=
l Override */ .bodyContent div a .yshortcuts /* Yahoo! Mail Override */{
=09=09=09=09/*@editable*/ color:#336699;
=09=09=09=09/*@editable*/ font-weight:normal;
=09=09=09=09/*@editable*/ text-decoration:underline;
=09=09=09}
=09=09=09
=09=09=09.bodyContent img{
=09=09=09=09display:inline;
=09=09=09=09height:auto;
=09=09=09}
=09=09=09
=09=09=09/* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: SIDEBAR /\/\/\/\/\/\/\/\=
/\/\ */
=09=09=09
=09=09=09/**
=09=09=09* @tab Sidebar
=09=09=09* @section sidebar style
=09=09=09* @tip Set the background color and border for your email's sideba=
r area.
=09=09=09*/
=09=09=09#templateSidebar{
=09=09=09=09/*@editable*/ background-color:#FFFFFF;
=09=09=09=09/*@editable*/ border-left:0;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Sidebar
=09=09=09* @section sidebar text
=09=09=09* @tip Set the styling for your email's sidebar text. Choose a siz=
e and color that is easy to read.
=09=09=09*/
=09=09=09.sidebarContent div{
=09=09=09=09/*@editable*/ color:#505050;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:12px;
=09=09=09=09/*@editable*/ line-height:150%;
=09=09=09=09/*@editable*/ text-align:left;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Sidebar
=09=09=09* @section sidebar link
=09=09=09* @tip Set the styling for your email's sidebar links. Choose a co=
lor that helps them stand out from your text.
=09=09=09*/
=09=09=09.sidebarContent div a:link, .sidebarContent div a:visited, /* Yaho=
o! Mail Override */ .sidebarContent div a .yshortcuts /* Yahoo! Mail Overri=
de */{
=09=09=09=09/*@editable*/ color:#336699;
=09=09=09=09/*@editable*/ font-weight:normal;
=09=09=09=09/*@editable*/ text-decoration:underline;
=09=09=09}
=09=09=09
=09=09=09.sidebarContent img{
=09=09=09=09display:inline;
=09=09=09=09height:auto;
=09=09=09}
=09=09=09
=09=09=09/* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: FOOTER /\/\/\/\/\/\/\/\/=
\/\ */
=09=09=09
=09=09=09/**
=09=09=09* @tab Footer
=09=09=09* @section footer style
=09=09=09* @tip Set the background color and top border for your email's fo=
oter area.
=09=09=09* @theme footer
=09=09=09*/
=09=09=09#templateFooter{
=09=09=09=09/*@editable*/ background-color:#FFFFFF;
=09=09=09=09/*@editable*/ border-top:0;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Footer
=09=09=09* @section footer text
=09=09=09* @tip Set the styling for your email's footer text. Choose a size=
 and color that is easy to read.
=09=09=09* @theme footer
=09=09=09*/
=09=09=09.footerContent div{
=09=09=09=09/*@editable*/ color:#707070;
=09=09=09=09/*@editable*/ font-family:Arial;
=09=09=09=09/*@editable*/ font-size:12px;
=09=09=09=09/*@editable*/ line-height:125%;
=09=09=09=09/*@editable*/ text-align:left;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Footer
=09=09=09* @section footer link
=09=09=09* @tip Set the styling for your email's footer links. Choose a col=
or that helps them stand out from your text.
=09=09=09*/
=09=09=09.footerContent div a:link, .footerContent div a:visited, /* Yahoo!=
 Mail Override */ .footerContent div a .yshortcuts /* Yahoo! Mail Override =
*/{
=09=09=09=09/*@editable*/ color:#336699;
=09=09=09=09/*@editable*/ font-weight:normal;
=09=09=09=09/*@editable*/ text-decoration:underline;
=09=09=09}
=09=09=09
=09=09=09.footerContent img{
=09=09=09=09display:inline;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Footer
=09=09=09* @section social bar style
=09=09=09* @tip Set the background color and border for your email's footer=
 social bar.
=09=09=09* @theme footer
=09=09=09*/
=09=09=09#social{
=09=09=09=09/*@editable*/ background-color:#FAFAFA;
=09=09=09=09/*@editable*/ border:0;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Footer
=09=09=09* @section social bar style
=09=09=09* @tip Set the background color and border for your email's footer=
 social bar.
=09=09=09*/
=09=09=09#social div{
=09=09=09=09/*@editable*/ text-align:center;
=09=09=09}
=09=09=09
=09=09=09/**
=09=09=09* @tab Footer
=09=09=09* @section utility bar style
=09=09=09* @tip Set the background color and border for your email's footer=
 utility bar.
=09=09=09* @theme footer
=09=09=09*/
=09=09=09#utility{
=09=09=09=09/*@editable*/ background-color:#FFFFFF;
=09=09=09=09/*@editable*/ border:0;
=09=09=09}

=09=09=09/**
=09=09=09* @tab Footer
=09=09=09* @section utility bar style
=09=09=09* @tip Set the background color and border for your email's footer=
 utility bar.
=09=09=09*/
=09=09=09#utility div{
=09=09=09=09/*@editable*/ text-align:center;
=09=09=09}
=09=09=09
=09=09=09#monkeyRewards img{
=09=09=09=09max-width:190px;
=09=09=09}
-->
</style>
<table border=3D"0" cellpadding=3D"0" cellspacing=3D"0" height=3D"100%" id=
=3D"backgroundTable" width=3D"100%">
=09<tbody>
=09=09<tr>
=09=09=09<td align=3D"center" valign=3D"top"><!-- // Begin Template Prehead=
er \\ -->
=09=09=09<table border=3D"0" cellpadding=3D"10" cellspacing=3D"0" id=3D"tem=
platePreheader" width=3D"600">
=09=09=09=09<tbody>
=09=09=09=09=09<tr>
=09=09=09=09=09=09<td class=3D"preheaderContent" valign=3D"top"><!-- // Beg=
in Module: Standard Preheader \ -->
=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"10" cellspacing=3D"0" =
width=3D"100%">
=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09<td valign=3D"top">
=09=09=09=09=09=09=09=09=09<div>Dear Matt Molyneaux,&nbsp;here&#39;s your n=
ewsletter from the frontline of digital rights: defending and promoting cit=
izens&#39; rights in the digital age.<br />
=09=09=09=09=09=09=09=09=09This update and previous versions are now availa=
ble from our website: <a href=3D"https://www.openrightsgroup.org/support-or=
g/">https://www.openrightsgroup.org/support-org/</a></div>
=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09<!-- *|IFNOT:ARCHIVE_PAGE|* -->
=09=09=09=09=09=09=09=09=09<td valign=3D"top" width=3D"190">
=09=09=09=09=09=09=09=09=09<div>&nbsp;</div>
=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09<!-- *|END:IF|* -->
=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09</table>
=09=09=09=09=09=09<!-- // End Module: Standard Preheader \ --></td>
=09=09=09=09=09</tr>
=09=09=09=09</tbody>
=09=09=09</table>
=09=09=09<!-- // End Template Preheader \\ -->

=09=09=09<table border=3D"0" cellpadding=3D"0" cellspacing=3D"0" id=3D"temp=
lateContainer" width=3D"600">
=09=09=09=09<tbody>
=09=09=09=09=09<tr>
=09=09=09=09=09=09<td align=3D"center" valign=3D"top"><!-- // Begin Templat=
e Header \\ -->
=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"0" cellspacing=3D"0" i=
d=3D"templateHeader" width=3D"600">
=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09<td class=3D"headerContent"><!-- // Begin Module=
: Standard Header Image \\ --><img border=3D"0" id=3D"headerImage campaign-=
icon" src=3D"http://www.openrightsgroup.org/assets/images/email/org-email.g=
if" style=3D"max-width: 600px;" /> <!-- // End Module: Standard Header Imag=
e \\ --></td>
=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09</table>
=09=09=09=09=09=09<!-- // End Template Header \\ --></td>
=09=09=09=09=09</tr>
=09=09=09=09=09<tr>
=09=09=09=09=09=09<td align=3D"center" valign=3D"top"><!-- // Begin Templat=
e Body \\ -->
=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"0" cellspacing=3D"0" i=
d=3D"templateBody" width=3D"600">
=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09<td valign=3D"top">
=09=09=09=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"0" cellspacin=
g=3D"0">
=09=09=09=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09<td class=3D"bodyContent" valign=3D"top=
">
=09=09=09=09=09=09=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"20" =
cellspacing=3D"0" height=3D"1706" width=3D"414">
=09=09=09=09=09=09=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td valign=3D"top">
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<style type=3D"text/css"><!--
P { margin-bottom: 0.21cm; }A:link {  }
-->
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</style>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<style type=3D"text/css"><!--
 /* Font Definitions */
@font-face
=09{font-family:Times;
=09panose-1:2 0 5 0 0 0 0 0 0 0;
=09mso-font-charset:0;
=09mso-generic-font-family:auto;
=09mso-font-pitch:variable;
=09mso-font-signature:3 0 0 0 1 0;}
@font-face
=09{font-family:"=C3=AF=C2=BC=C2=AD=C3=AF=C2=BC=C2=B3 =C3=A6=CB=9C=C5=BD=C3=
=A6=C5=93=C2=9D";
=09mso-font-charset:78;
=09mso-generic-font-family:auto;
=09mso-font-pitch:variable;
=09mso-font-signature:1 134676480 16 0 131072 0;}
@font-face
=09{font-family:"Cambria Math";
=09panose-1:2 4 5 3 5 4 6 3 2 4;
=09mso-font-charset:0;
=09mso-generic-font-family:auto;
=09mso-font-pitch:variable;
=09mso-font-signature:-536870145 1107305727 0 0 415 0;}
@font-face
=09{font-family:Cambria;
=09panose-1:2 4 5 3 5 4 6 3 2 4;
=09mso-font-charset:0;
=09mso-generic-font-family:auto;
=09mso-font-pitch:variable;
=09mso-font-signature:-536870145 1073743103 0 0 415 0;}
 /* Style Definitions */
p.MsoNormal, li.MsoNormal, div.MsoNormal
=09{mso-style-unhide:no;
=09mso-style-qformat:yes;
=09mso-style-parent:"";
=09margin:0cm;
=09margin-bottom:.0001pt;
=09mso-pagination:widow-orphan;
=09font-size:12.0pt;
=09font-family:Cambria;
=09mso-ascii-font-family:Arial;
=09mso-ascii-theme-font:minor-latin;
=09mso-fareast-font-family:"=C3=AF=C2=BC=C2=AD=C3=AF=C2=BC=C2=B3 =C3=A6=CB=
=9C=C5=BD=C3=A6=C5=93=C2=9D";
=09mso-fareast-theme-font:minor-fareast;
=09mso-hansi-font-family:Cambria;
=09mso-hansi-theme-font:minor-latin;
=09mso-bidi-font-family:"Times New Roman";
=09mso-bidi-theme-font:minor-bidi;
=09mso-ansi-language:EN-US;}
p
=09{mso-style-priority:99;
=09mso-margin-top-alt:auto;
=09margin-right:0cm;
=09mso-margin-bottom-alt:auto;
=09margin-left:0cm;
=09mso-pagination:widow-orphan;
=09font-size:14px;
=09font-family:Arial;
=09mso-fareast-font-family:"=C3=AF=C2=BC=C2=AD=C3=AF=C2=BC=C2=B3 =C3=A6=CB=
=9C=C5=BD=C3=A6=C5=93=C2=9D";
=09mso-fareast-theme-font:minor-fareast;
=09mso-bidi-font-family:"Times New Roman";}
.MsoChpDefault
=09{mso-style-type:export-only;
=09mso-default-props:yes;
=09font-family:Cambria;
=09mso-ascii-font-family:Cambria;
=09mso-ascii-theme-font:minor-latin;
=09mso-fareast-font-family:"=C3=AF=C2=BC=C2=AD=C3=AF=C2=BC=C2=B3 =C3=A6=CB=
=9C=C5=BD=C3=A6=C5=93=C2=9D";
=09mso-fareast-theme-font:minor-fareast;
=09mso-hansi-font-family:Cambria;
=09mso-hansi-theme-font:minor-latin;
=09mso-bidi-font-family:"Times New Roman";
=09mso-bidi-theme-font:minor-bidi;
=09mso-ansi-language:EN-US;}
@page WordSection1
=09{size:612.0pt 792.0pt;
=09margin:72.0pt 90.0pt 72.0pt 90.0pt;
=09mso-header-margin:36.0pt;
=09mso-footer-margin:36.0pt;
=09mso-paper-source:0;}
div.WordSection1
=09{page:WordSection1;}
-->
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</style>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<h2>Paris attack</h2>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09We&#39;d planned to send an em=
ail about the Investigatory Powers Bill earlier this week. After the horrif=
ic attacks on Friday, it just didn&#39;t feel right. We didn&#39;t really w=
ant to campaign or comment on surveillance in the UK.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09But over the last couple of da=
ys, we&#39;ve heard politicians call for the IPB to be fast tracked through=
 Parliament and we&rsquo;ve been asked what we think of this. We understand=
 that people are rightly concerned about surveillance powers in the UK, but=
 this is not the time to rush through legislation.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09The Paris attacks were not jus=
t brutal murders but an assault on our freedom and liberty. We cannot let t=
errorists undermine our fundamental values through a knee-jerk reaction to =
these terrible events.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Interestingly, we appear to be=
 in agreement with the Home Secretary, Theresa May who said this week:<br /=
>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<em>&#39;The draft Investigato=
ry Powers Bill is a significant measure that we expect to stand the test of=
 time. We do not want future Governments to have to change investigatory po=
wers legislation constantly, so it is important that we get it right. It is=
 therefore important that the Bill receives proper scrutiny and that it has=
 support across the House, given the nature of it.&#39;</em><br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09So we&#39;re sending this emai=
l because it&#39;s important that we get on and scrutinise this Bill and sp=
eak out against that the parts that undermine our fundamental rights. As ev=
er, we are going to need your help to do this.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09&nbsp;
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<h2>What&#39;s the status of t=
he IPB?</h2>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Although some politicians, lik=
e Lord Carlisle, called for the Investigatory Powers Bill to be fast-tracke=
d this week, it is currently scheduled to still follow the proper process.<=
br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09This means that there is an op=
portunity for the a full discussion about surveillance, the one we&#39;ve b=
een calling for these past years.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09What happens next is that a co=
mmittee of MPs and Lords will scrutinise the Bill. ORG will provide evidenc=
e to that Committee, and we&rsquo;ll help you do so too.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09When that stage is over, they =
will report in the new year with suggestions for changes to the Bill.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09We then expect MPs to vote on =
the final version in spring. This is why it is important to <a href=3D"http=
s://www.openrightsgroup.org/campaigns/investigatory-powers-bill-email-your-=
mp">start talking to them now</a>; so they are aware of the concerns that t=
heir constituents have about the Bill, and to get them to pay attention to =
this huge piece of surveillance law.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09&nbsp;
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<h2>Take action today!</h2>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09The people scrutinising the la=
w are not working in a bubble. They listen to colleagues and their leadersh=
ip. They listen to the voices around them and how the public is thinking.<b=
r />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09You can help influence them by=
 asking your MP to talk to members of those committees. We all need to star=
t talking to MPs now to get them thinking about the IPB.&nbsp;<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09You can tell your MP why they =
should be concerned about the Bill here:<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<a href=3D"https://www.openrig=
htsgroup.org/campaigns/investigatory-powers-bill-email-your-mp">https://www=
.openrightsgroup.org/campaigns/investigatory-powers-bill-email-your-mp</a><=
br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09This is only the start of the =
campaign. We&#39;ve already been talking to politicians and the media about=
 the IPB. We met with Andy Burnham, Shadow Home Secretary and other Labour =
politicians this week to discuss our concerns.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09In the coming months, we&#39;l=
l be working together with you to rip out the dangerous parts of this Bill.=
 We can do this! &nbsp;<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09&nbsp;
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<h2 dir=3D"ltr">What&#39;s in =
the Bill?</h2>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09The Investigatory Powers Bill =
is a new law on surveillance that was presented to parliament in November 2=
015. Unlike the Communications Data Bill, the IPB covers both the police an=
d security services&rsquo; powers. &nbsp;<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<strong>Key issues in the Bill=
</strong> &nbsp;<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09-It clarifies the powers of se=
curity agencies to break into our laptops and mobile phones, including powe=
rs for mass hacking. The Bill also forces internet companies to help in hac=
king their customers.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09-It forces Internet Service Pr=
oviders to collect and keep a record of all the websites that their custome=
rs visit.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09-It does not limit the mass su=
rveillance revealed by Edward Snowden, but instead puts those abilities int=
o law.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09This includes powers of bulk c=
ollection and analysis of data collected by tapping Internet cables, ie. &#=
39;<a href=3D"https://wiki.openrightsgroup.org/wiki/Tempora">Tempora</a>&#3=
9;.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09We&rsquo;ll be publishing a fu=
ll briefing on the Bill to help you talk to your MP.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09&nbsp;
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<h2 dir=3D"ltr">Our Birthday p=
arty</h2>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09ORG has worked hard over the l=
ast 10 years to ensure that everyone&rsquo;s rights are protected (You can =
see a whole timeline of our successes <a data-mce-href=3D"ourwork/successes=
/" href=3D"https://www.openrightsgroup.org/ourwork/successes/">here)</a>.<b=
r />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Now we&rsquo;re celebrating th=
at history with a small party in London, and we&rsquo;d love it if you coul=
d make it to celebrate with us! RSVP:<a data-mce-href=3D"http://www.meetup.=
com/ORG-London/events/226537708/" href=3D"http://www.meetup.com/ORG-London/=
events/226537708/"> http://www.meetup.com/ORG-London/events/226537708/</a><=
br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Date: November 27th<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Time: 7.00 - 10.00pm<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Location:<a data-mce-href=3D"h=
ttp://maps.google.com/maps?f=3Dq&amp;hl=3Den&amp;q=3D133-135+Bethnal+Green+=
Road%2C+E2+7DG%2C+London%2C+gb" href=3D"http://maps.google.com/maps?f=3Dq&a=
mp;hl=3Den&amp;q=3D133-135+Bethnal+Green+Road%2C+E2+7DG%2C+London%2C+gb"> N=
ewspeak House</a>, 133-135 Bethnal Green Road, E2 7DG, London<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Cost: &pound;5 Hear from an ex=
cellent speaker and enjoy some birthday cake at the brand new Newspeak Hous=
e in Shoreditch for our 10th anniversary!
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br></br>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<h1><strong>Get Involved</stro=
ng></h1>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09It&rsquo;s our job to stand up=
 for your rights online. If you have a moment to spare can you help us by <=
a _mce_href=3D"http://www.openrightsgroup.org/join" href=3D"http://www.open=
rightsgroup.org/join">becoming a member of ORG</a>?<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09You can find out about more wa=
ys to get involved here:<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<a href=3D"https://www.openrig=
htsgroup.org/get-involved">https://www.openrightsgroup.org/get-involved</a>=
<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Thank you for supporting digit=
al rights.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Best wishes,<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Ruth&nbsp;&nbsp; &nbsp;</td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09=09=09=09=09=09=09</table>
=09=09=09=09=09=09=09=09=09=09=09=09<!-- // End Module: Standard Content \\=
 --></td>
=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09=09=09=09</table>
=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09<!-- // Begin Sidebar \\  -->
=09=09=09=09=09=09=09=09=09<td id=3D"templateSidebar" valign=3D"top" width=
=3D"200">
=09=09=09=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"0" cellspacin=
g=3D"0" width=3D"200">
=09=09=09=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09<td class=3D"sidebarContent" valign=3D"=
top"><!-- // Begin Module: Social Block with Icons \\ -->
=09=09=09=09=09=09=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"0" c=
ellspacing=3D"0" width=3D"100%">
=09=09=09=09=09=09=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td style=3D"padding-top: 10px=
; padding-right: 20px; padding-left: 20px;" valign=3D"top">
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<table border=3D"0" cellpaddin=
g=3D"0" cellspacing=3D"4">
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td align=3D"left" va=
lign=3D"middle" width=3D"16"><img border=3D"0" src=3D"https://gallery.mailc=
himp.com/653153ae841fd11de66ad181a/images/sfs_icon_facebook.png" style=3D"m=
argin: 0 !important;" /></td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td align=3D"left" va=
lign=3D"top">
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<div><a href=3D"https=
://www.facebook.com/openrightsgroup">Find us on Facebook</a></div>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td align=3D"left" va=
lign=3D"middle" width=3D"16"><img border=3D"0" src=3D"http://gallery.mailch=
imp.com/653153ae841fd11de66ad181a/images/sfs_icon_twitter.png" style=3D"mar=
gin: 0 !important;" /></td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td align=3D"left" va=
lign=3D"top">
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<div><a href=3D"https=
://twitter.com/openrightsgroup">Follow us on Twitter</a></div>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td align=3D"left" va=
lign=3D"middle" width=3D"16"><img border=3D"0" height=3D"16" src=3D"https:/=
/www.openrightsgroup.org/assets/images/social/g+250.png" style=3D"margin: 0=
px ! important; border: 0px none;" width=3D"16" /></td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td align=3D"left" va=
lign=3D"top">
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<div><a href=3D"https=
://plus.google.com/116543318055985390327/posts">Add us on Google+</a></div>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</table>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09=09=09=09=09=09=09</table>
=09=09=09=09=09=09=09=09=09=09=09=09<!-- // End Module: Social Block with I=
cons \\ --><!-- // Begin Module: Top Image with Content \\ -->

=09=09=09=09=09=09=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"20" =
cellspacing=3D"0" height=3D"1541" width=3D"213">
=09=09=09=09=09=09=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<td valign=3D"top">
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<h2>Quick Fire News</h2>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<strong>We&#39;d like to welco=
me our latest corporate supporters, </strong><a href=3D"https://www.isotoma=
.com/">Isotoma</a>, <a href=3D"https://www.uno.net.uk/">Uno</a>, <a href=3D=
"http://www.numbergroup.com/">Numbergroup</a> and <a href=3D"https://www.vp=
ncompare.co.uk/">VPN Compare</a>, and thank them for supporting us in our c=
ampaigning for digital rights.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<strong>Our groups in Sheffiel=
d and Edinburgh</strong> have been meeting this week to discuss the Investi=
gatory Powers Bill and plan local campaigns together.<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09&nbsp;
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<h3><strong>ORG out and about<=
/strong></h3>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<strong><a href=3D"http://www.=
meetup.com/ORG-London/events/226537708/">ORG&#39;s 10th Anniversary Party</=
a></strong><br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09Friday 27th November<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<span class=3D"subtext">7 PM</=
span> <span class=3D"subtext">to</span> <span class=3D"subtext">10:00 PM</s=
pan><br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<a data-mce-href=3D"http://map=
s.google.com/maps?f=3Dq&amp;hl=3Den&amp;q=3D133-135+Bethnal+Green+Road%2C+E=
2+7DG%2C+London%2C+gb" href=3D"http://maps.google.com/maps?f=3Dq&amp;hl=3De=
n&amp;q=3D133-135+Bethnal+Green+Road%2C+E2+7DG%2C+London%2C+gb">Newspeak Ho=
use</a>, 133-135 Bethnal Green Road, E2 7DG, London<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09<br />
=09=09=09=09=09=09=09=09=09=09=09=09=09=09=09&nbsp;</td>
=09=09=09=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09=09=09=09=09=09=09</table>
=09=09=09=09=09=09=09=09=09=09=09=09<!-- // End Module: Top Image with Cont=
ent \\ --></td>
=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09=09=09=09</table>
=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09<!-- // End Sidebar \\ -->
=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09</table>
=09=09=09=09=09=09<!-- // End Template Body \\ --></td>
=09=09=09=09=09</tr>
=09=09=09=09=09<tr>
=09=09=09=09=09=09<td align=3D"center" valign=3D"top"><!-- // Begin Templat=
e Footer \\ -->
=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"10" cellspacing=3D"0" =
id=3D"templateFooter" width=3D"600">
=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09<td class=3D"footerContent" valign=3D"top"><!-- =
// Begin Module: Standard Footer \\ -->
=09=09=09=09=09=09=09=09=09<table border=3D"0" cellpadding=3D"10" cellspaci=
ng=3D"0" width=3D"100%">
=09=09=09=09=09=09=09=09=09=09<tbody>
=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09<td colspan=3D"2" id=3D"social" valign=
=3D"middle">
=09=09=09=09=09=09=09=09=09=09=09=09<div>&nbsp;<a href=3D"https://twitter.c=
om/openrightsgroup">Follow us on Twitter</a> | <a href=3D"https://www.faceb=
ook.com/openrightsgroup">Find us on Facebook</a> | <a href=3D"https://plus.=
google.com/116543318055985390327/posts">Add us on Google+</a> &nbsp;</div>
=09=09=09=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09<td valign=3D"top" width=3D"350">
=09=09=09=09=09=09=09=09=09=09=09=09<div><a href=3D"https://www.openrightsg=
roup.org/volunteer" title=3D"Volunteer">We need your help</a> to fight for =
your rights and to keep the web open and free.</div>
=09=09=09=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09=09=09=09<td id=3D"monkeyRewards" valign=3D"top"=
 width=3D"190">
=09=09=09=09=09=09=09=09=09=09=09=09<div><strong>Our mailing address is:</s=
trong></div>

=09=09=09=09=09=09=09=09=09=09=09=09<div>12 Tileyard Road<br />
=09=09=09=09=09=09=09=09=09=09=09=09London<br />
=09=09=09=09=09=09=09=09=09=09=09=09N7 9AH</div>
=09=09=09=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09=09<tr>
=09=09=09=09=09=09=09=09=09=09=09=09<td colspan=3D"2" id=3D"utility" valign=
=3D"middle">
=09=09=09=09=09=09=09=09=09=09=09=09<div>This email was delivered to: mogge=
rs87@m87.co.uk; If you wish to opt out of future emails, you can do so <a h=
ref=3D"https://www.openrightsgroup.org/unsubscribe">here</a>.&nbsp;| <a hre=
f=3D"https://www.openrightsgroup.org/join">Join ORG</a>&nbsp;</div>
=09=09=09=09=09=09=09=09=09=09=09=09</td>
=09=09=09=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09=09=09=09</table>
=09=09=09=09=09=09=09=09=09<!-- // End Module: Standard Footer \\ --></td>
=09=09=09=09=09=09=09=09</tr>
=09=09=09=09=09=09=09</tbody>
=09=09=09=09=09=09</table>
=09=09=09=09=09=09<!-- // End Template Footer \\ --></td>
=09=09=09=09=09</tr>
=09=09=09=09</tbody>
=09=09=09</table>
=09=09=09</td>
=09=09</tr>
=09</tbody>
</table>
</body>
</html>
<img alt=3D"supporter" src=3D"https://www.e-activist.com/ea-action/broadcas=
t.record.message.open.do?ea.broadcast.id=3D95540&ea.campaigner.id=3DvYXku28=
i3E4=3D&ea.client.id=3D1422"/>
------=_Part_29748709_1445524343.1448020924829--

------=_Part_29748710_445134290.1448020924829--
"""


EXAMPLE_DIGEST = """Content-Type: multipart/mixed; boundary="===============1488510984=="
MIME-Version: 1.0
From: centos-announce-request@centos.org
Subject: CentOS-announce Digest, Vol 109, Issue 3
To: centos-announce@centos.org
Reply-To: centos-announce@centos.org
Date: Mon, 10 Mar 2014 12:00:04 +0000
Message-ID: <mailman.12.1394452804.11046.centos-announce@centos.org>
X-BeenThere: centos-announce@centos.org
X-Mailman-Version: 2.1.9
Precedence: list
List-Id: "CentOS announcements \(security and general\) will be posted to
 this list." <centos-announce.centos.org>
List-Unsubscribe:
 <http://lists.centos.org/mailman/listinfo/centos-announce>, 
 <mailto:centos-announce-request@centos.org?subject=unsubscribe>
List-Archive: <http://lists.centos.org/pipermail/centos-announce>
List-Post: <mailto:centos-announce@centos.org>
List-Help: <mailto:centos-announce-request@centos.org?subject=help>
List-Subscribe: <http://lists.centos.org/mailman/listinfo/centos-announce>,
 <mailto:centos-announce-request@centos.org?subject=subscribe>
Sender: centos-announce-bounces@centos.org
Errors-To: centos-announce-bounces@centos.org


--===============1488510984==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Description: CentOS-announce Digest, Vol 109, Issue 3

Send CentOS-announce mailing list submissions to
        centos-announce@centos.org

To subscribe or unsubscribe via the World Wide Web, visit
        http://lists.centos.org/mailman/listinfo/centos-announce
or, via email, send a message with subject or body 'help' to
        centos-announce-request@centos.org

You can reach the person managing the list at
        centos-announce-owner@centos.org

When replying, please edit your Subject line so it is more specific
than "Re: Contents of CentOS-announce digest..."

--===============1488510984==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Description: Today's Topics (2 messages)

Today's Topics:

   1. CEBA-2014:0262  CentOS 6 qemu-kvm Update (Johnny Hughes)
   2. CEBA-2014:0264  CentOS 6 libtirpc Update (Johnny Hughes)

--===============1488510984==
Content-Type: multipart/digest; boundary="===============0249781194=="
MIME-Version: 1.0


--===============0249781194==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Mon, 10 Mar 2014 11:21:06 +0000
Reply-To: centos@centos.org
Message-ID: <20140310112106.GA24758@n04.lon1.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CEBA-2014:0262  CentOS 6 qemu-kvm Update
Message: 1


CentOS Errata and Bugfix Advisory 2014:0262 

Upstream details at : https://rhn.redhat.com/errata/RHBA-2014-0262.html

The following updated files have been uploaded and are currently 
syncing to the mirrors: ( sha256sum Filename ) 

i386:
46164fd539f764d60217ca6193928d37e8ab3ae1be81ae833b15f866de5fedd0  qemu-guest-agent-0.12.1.2-2.415.el6_5.5.i686.rpm

x86_64:
aed574e07f0992175f9777787991b664d1cf72c8e0d563e7d58185282ce3f8c4  qemu-guest-agent-0.12.1.2-2.415.el6_5.5.x86_64.rpm
0885b34016bdc113d1dff172d9835aec6ae4dc5919243ec7cb707cbebc607527  qemu-img-0.12.1.2-2.415.el6_5.5.x86_64.rpm
01109b5adab7bf10e5b81c670838160e74a60ee75561e971fca378773ff3941a  qemu-kvm-0.12.1.2-2.415.el6_5.5.x86_64.rpm
7e2e6e07951b8611473551f983eabaf60e3a649e8a04cc933ea47aa3b94f0479  qemu-kvm-tools-0.12.1.2-2.415.el6_5.5.x86_64.rpm

Source:
9abd731cd3600b76507b3c1911fc89464c6f29d37b04f349d3a684812e66f402  qemu-kvm-0.12.1.2-2.415.el6_5.5.src.rpm



-- 
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net



--===============0249781194==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Mon, 10 Mar 2014 11:21:45 +0000
Reply-To: centos@centos.org
Message-ID: <20140310112145.GA24853@n04.lon1.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CEBA-2014:0264  CentOS 6 libtirpc Update
Message: 2


CentOS Errata and Bugfix Advisory 2014:0264 

Upstream details at : https://rhn.redhat.com/errata/RHBA-2014-0264.html

The following updated files have been uploaded and are currently 
syncing to the mirrors: ( sha256sum Filename ) 

i386:
0232079882c8a0f3cdd00417b0fdfc45fdb2f2066d7bd35a2b127658be6f8d94  libtirpc-0.2.1-6.el6_5.1.i686.rpm
0fc6cd31c479c01b3bd4d3a6c62fd04ec8a4429708ef10e41633b628f0771fb4  libtirpc-devel-0.2.1-6.el6_5.1.i686.rpm

x86_64:
0232079882c8a0f3cdd00417b0fdfc45fdb2f2066d7bd35a2b127658be6f8d94  libtirpc-0.2.1-6.el6_5.1.i686.rpm
8fbe3e9cc0f83dd10b6a34c6d37695dccf9968c74177f8cb676467dbd82678fe  libtirpc-0.2.1-6.el6_5.1.x86_64.rpm
0fc6cd31c479c01b3bd4d3a6c62fd04ec8a4429708ef10e41633b628f0771fb4  libtirpc-devel-0.2.1-6.el6_5.1.i686.rpm
9fae583a5e8b1520f5a4982348fa00ce602b0d76e7a01a560e92314f66609385  libtirpc-devel-0.2.1-6.el6_5.1.x86_64.rpm

Source:
1ab0d65c11a4a51a88c7d03884e8f052745fc6778f276731f574ad510dd58185  libtirpc-0.2.1-6.el6_5.1.src.rpm



-- 
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net



--===============0249781194==--

--===============1488510984==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Description: Digest Footer

_______________________________________________
CentOS-announce mailing list
CentOS-announce@centos.org
http://lists.centos.org/mailman/listinfo/centos-announce

--===============1488510984==--
"""


EXAMPLE_ALT = """Return-Path: <newsletter@gog.com>
Delivered-To: <moggers87@thewarof1812.moggers.co.uk>
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=gog.com; s=klucz;
 t=1447440216; bh=l0Buq2T4lA4iqsJXfCC7G7rWIFHCulVCxCZqR2SZ+fM=;
 h=Message-ID:Date:Subject:From:To:MIME-Version:Content-Type;
 b=juTZflTGwCds0wFc3buBIBf9BEcXXVHgccqqj9jYORHZIvDyk/BAsP3QtGVqjx26x
 uC03bainzJUEhkyIglgArcuC23qmv8MCQ2koRs4VG4FT6QZvhdSOK6fwPNyF5IvyJx
 klNUMrdiwvF4mkFp3FdZeHcFLXxD1p/mIRF/FOpk=
Message-ID: <1447440216.56462f5827cb6@swift.generated>
Date: Fri, 13 Nov 2015 20:43:36 +0200
Subject: The Big Fall Sale Finale starts now! Only 48 hours left!
From: "GOG.com Team" <newsletter@gog.com>
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="_=_swift_v4_144744021656462f582810e_=_"
To: example@example.com


--_=_swift_v4_144744021656462f582810e_=_
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable

If you can see this text it means that your email client couldn't displa=
y our newsletter properly.
Please visit this link to view the newsle=
tter on our website: http://www.gog.com/newsletter/fall_promo_finale_131=
115_en

- GOG.com Team


--_=_swift_v4_144744021656462f582810e_=_
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
                                        =
<html>
                                            <head>
                                                <title>The Big Fall Sale Fin=
ale starts now! Only 48 hours left!</title>
                                                <meta http-e=
quiv=3D"content-type" content=3D"text/html;charset=3Dutf-8" />
                                                <=
/head><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://w=
ww.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns=3D"http://w=
ww.w3.org/1999/xhtml">
 <head>
 <meta http-equiv=3D"Content-Ty=
pe" content=3D"text/html; charset=3Dutf-8" />
 <meta name=3D"viewport"=
 content=3D"width=3D720, initial-scale=3D1.0" />
 <style>table a, tabl=
e a:link, table a:visited { color: #808080; boder: none; } img { border:=
none; } body { background: #2d2d2d; line-height: 0px;} </style>
 </he=
ad>
 <body>
 <!-- ---WEB--- -->
 <table bgcolor=3D"#2d2d2d"=
 style=3D"background-color: #2d2d2d; text-align: center; margin: 0px auto;=
 padding: 0px;" width=3D"99%">
 <tr>
 <td> </td>
 <td alig=
n=3D"center" width=3D"600" >
 <table cellpadding=3D"0" cellspacing=
=3D"0" width=3D"600" style=3D"COLOR: #7b7b7b; line-height: 11px; font-fami=
ly: Tahoma, Verdana, Arial, Helvetica, sans-serif; margin: 0px; padding:=
 0px">
 <tr valign=3D"top" style=3D"margin: 0; padding: 0;">
 <t=
d width=3D"600" height=3D"66" colspan=3D"2">
 <table cellpadding=3D"=
0" cellspacing=3D"0" width=3D"600" class=3D"wwwno">
 <tr valign=3D"t=
op" style=3D"margin: 0; padding: 0;">
 <td width=3D"48" align=3D"le=
ft"><a href=3D"http://www.gog.com"><img style=3D"border: 0;" src=3D"http:/=
/static.gog.com/upload/newsletters/img/gog-logo-white-41.jpg" height=3D"46=
" /></a></td>
 <td width=3D"10" style=3D"font-size: 0; width: 10px;"=
>=C2=A0</td>
 <td width=3D"542" valign=3D"middle" align=3D"right=
">
 <span style=3D"margin: 0px; padding: 0px; color: #808080; font-siz=
e: 11px; line-height: 11px; font-family: Tahoma, Verdana, Arial, Helveti=
ca, sans-serif;">Up to 90% off<br /><a style=3D"color: #808080; cursor: po=
inter; text-decoration: underline; font-weight: normal;" href=3D"http://ww=
w.gog.com/newsletter/fall_promo_finale_131115_en?utm_source=3Dnewsletter&u=
tm_medium=3Demail&utm_content=3Dgame_subject&utm_campaign=3DBig_Fall_Final=
e_Main_EN">Problems viewing this email?</a></span>
 </td>
 </tr>=

 </table>
 </td>
 </tr>
 <tr valign=3D"top" style=
=3D"margin: 0; padding: 0; line-height: 0px;">
 <td width=3D"600" st=
yle=3D"font-size: 0;">
 <a href=3D"http://www.gog.com?utm_source=3Dnew=
sletter&utm_medium=3Demail&utm_content=3Dgame_subject&utm_campaign=3DBig_F=
all_Finale_Main_EN">
 <img src=3D"http://static.gog.com/upload/newslet=
ters/fall_promo_finale_131115_en/en/img/fpf_03.jpg" height=3D"214" alt=
=3D"" style=3D"display:block; border:0;"/>
 </a>
 </td>
 =
</tr>
 <tr valign=3D"top" style=3D"margin: 0; padding: 0; line-heigh=
t: 0px;">
 <td width=3D"600" style=3D"font-size: 0;">
 <a hr=
ef=3D"http://www.gog.com?utm_source=3Dnewsletter&utm_medium=3Demail&utm_co=
ntent=3Dgame_subject&utm_campaign=3DBig_Fall_Finale_Main_EN">
 <img =
src=3D"http://static.gog.com/upload/newsletters/fall_promo_finale_131115_e=
n/en/img/fpf_05.jpg" height=3D"215" alt=3D"" style=3D"display:block; borde=
r:0;"/>
 </a>
 </td>
 </tr>
 <tr valign=3D"top" styl=
e=3D"margin: 0; padding: 0; line-height: 0px;">
 <td width=3D"600" s=
tyle=3D"font-size: 0;">
 <a href=3D"http://www.gog.com?utm_source=3Dne=
wsletter&utm_medium=3Demail&utm_content=3Dgame_subject&utm_campaign=3DBig_=
Fall_Finale_Main_EN">
 <img src=3D"http://static.gog.com/upload/newsle=
tters/fall_promo_finale_131115_en/en/img/fpf_06.jpg" height=3D"214" al=
t=3D"" style=3D"display:block; border:0;"/>
 </a>
 </td>
 =
</tr>
 <tr valign=3D"top" style=3D"margin: 0; padding: 0; line-heigh=
t: 0px;">
 <td width=3D"600" height=3D"45" style=3D"font-size: 0;"> </=
td>
 </tr>
 <tr valign=3D"top" style=3D"margin: 0; padding: 0; li=
ne-height: 0px;">
 <td width=3D"600" style=3D"font-size: 0;">
 <=
a href=3D"http://www.gog.com?utm_source=3Dnewsletter&utm_medium=3Demail&ut=
m_content=3Dgame_subject&utm_campaign=3DBig_Fall_Finale_EN">
 <img s=
rc=3D"http://static.gog.com/upload/newsletters/fall_promo_finale_131115_en=
/en/img/fpf_08.jpg" height=3D"142" alt=3D"" style=3D"display:block; border=
:0;"/>
 </a>
 </td>
 </tr>
 <tr valign=3D"top" styl=
e=3D"margin: 0; padding: 0; line-height: 0px;">
 <td width=3D"600" s=
tyle=3D"font-size: 0;">
 <a href=3D"http://www.gog.com?utm_source=3Dne=
wsletter&utm_medium=3Demail&utm_content=3Dgame_subject&utm_campaign=3DBig_=
Fall_Finale_EN">
 <img src=3D"http://static.gog.com/upload/newsletters=
/fall_promo_finale_131115_en/en/img/fpf_09.jpg" height=3D"102" alt=3D"" =
style=3D"display:block; border:0;"/>
 </a>
 </td>
 </tr=
>
 <tr valign=3D"top" style=3D"margin: 0; padding: 0; line-height: 0=
px;">
 <td width=3D"600" height=3D"45" style=3D"font-size: 0;"> </=
td>
 </tr>
=20
 <tr valign=3D"top" style=3D"margin: 0; paddi=
ng: 0; line-height: 0px;">
 <td width=3D"600" style=3D"font-size: 0;=
">
 <a href=3D"http://www.gog.com?utm_source=3Dnewsletter&utm_medium=
=3Demail&utm_content=3Dgame_subject&utm_campaign=3DBig_Fall_Finale_EN"=
>
 <img src=3D"http://static.gog.com/upload/newsletters/fall_promo_fin=
ale_131115_en/en/img/fpf_11.jpg" height=3D"318" alt=3D"" style=3D"display:=
block; border:0;"/>
 </a>
 </td>
 </tr>
 <tr valig=
n=3D"top" style=3D"margin: 0; padding: 0; line-height: 0px;">
 <td w=
idth=3D"600" style=3D"font-size: 0;">
 <a href=3D"http://www.gog.com?u=
tm_source=3Dnewsletter&utm_medium=3Demail&utm_content=3Dgame_subject&utm_c=
ampaign=3DBig_Fall_Finale_EN">
 <img src=3D"http://static.gog.com/up=
load/newsletters/fall_promo_finale_131115_en/en/img/fpf_12.jpg" height=3D"=
232" alt=3D"" style=3D"display:block; border:0;"/>
 </a>
 </=
td>
 </tr>
 <tr valign=3D"top" style=3D"margin: 0; padding: 0; li=
ne-height: 0px;">
 <td width=3D"600" style=3D"font-size: 0;">
 <=
a href=3D"http://www.gog.com?utm_source=3Dnewsletter&utm_medium=3Demail&ut=
m_content=3Dgame_subject&utm_campaign=3DBig_Fall_Finale_EN">
 <img s=
rc=3D"http://static.gog.com/upload/newsletters/fall_promo_finale_131115_en=
/en/img/fpf_13.jpg" height=3D"162" alt=3D"" style=3D"display:block; border=
:0;"/>
 </a>
 </td>
 </tr>
 <tr valign=3D"top" styl=
e=3D"margin: 0; padding: 0; line-height: 0px;">
 <td width=3D"600" h=
eight=3D"20" style=3D"font-size: 0;"> </td>
 </tr>
 <tr valig=
n=3D"top" style=3D"margin: 0; padding: 0;">
 <td width=3D"600" alig=
n=3D"left" valign=3D"top" style=3D"font-size: 9px; font-family: Tahoma, Ve=
rdana, Arial, Helvetica, sans-serif; text-align: left; color:#7B7B7B=
;">
 <a href=3D"http://www.gog.com" style=3D"text-decoration:none; cu=
rsor:default; color:#7B7B7B;">GOG.com</a> =C2=A9 2015. Part of CD PROJEKT=
 group.<br/> All other trademarks and copyrights are properties of their=
 respective owners.<br/>
 <span class=3D"wwwno">If you prefer not to r=
eceive newsletters from <a href=3D"http://www.gog.com" style=3D"text-dec=
oration:none; cursor:default; color:#7B7B7B;">GOG.com</a> <a style=3D"colo=
r: #7b7b7b; cursor: pointer; text-decoration: underline;" href=3D"http://w=
ww.gog.com/unsubscribe/6cX9ZIMVnDyHyR7kgc3H8k1lL5Oir1oIwTE|">click here<=
/a>.</span><br/>
 <span class=3D"wwwno">GOG Ltd, 7 Florinis Str., Greg=
 Tower, 6th Floor, 1065 Nicosia, Cyprus</span>
 </td>
 </tr>=

 <tr valign=3D"top" style=3D"margin: 0; padding: 0; line-height: 0p=
x;">
 <td width=3D"600" height=3D"20" style=3D"font-size: 0;"> </t=
d>
 </tr>
 </table>
 </td>
 <td> </td>
 </tr>=

 </table>
 <!-- ---WEB--- -->
 <!-- Litmus -->
 <sty=
le>@media print{ #_t { background-image: url('https://orx6fbfm.emltrk.co=
m/orx6fbfm?p&d=3D6cX9ZIMVnDyHyR7kgc3H8k1lL5Oir1oIwTE|');}} div.OutlookMess=
ageHeader {background-image:url('https://orx6fbfm.emltrk.com/orx6fbfm?f&=
d=3D6cX9ZIMVnDyHyR7kgc3H8k1lL5Oir1oIwTE|')} table.moz-email-headers-table =
{background-image:url('https://orx6fbfm.emltrk.com/orx6fbfm?f&d=3D6cX9ZIMV=
nDyHyR7kgc3H8k1lL5Oir1oIwTE|')} blockquote #_t {background-image:url('ht=
tps://orx6fbfm.emltrk.com/orx6fbfm?f&d=3D6cX9ZIMVnDyHyR7kgc3H8k1lL5Oir1oIw=
TE|')} #MailContainerBody #_t {background-image:url('https://orx6fbfm.em=
ltrk.com/orx6fbfm?f&d=3D6cX9ZIMVnDyHyR7kgc3H8k1lL5Oir1oIwTE|')}</style><di=
v id=3D"_t"></div>
 <img src=3D"https://orx6fbfm.emltrk.com/orx6fbfm=
?d=3D6cX9ZIMVnDyHyR7kgc3H8k1lL5Oir1oIwTE|" width=3D"1" height=3D"1" border=
=3D"0" />
 <!-- /Litmus -->
 </body>
</html>=20

--_=_swift_v4_144744021656462f582810e_=_--

"""


EXAMPLE_SIGNED_FORWARDED_DIGEST = """Message-ID: <1448059000.4758.0.camel@example.com>
Subject: [Fwd: CentOS-announce Digest, Vol 108, Issue 9]
From: Matt Molyneaux <example@example.com>
To: Matt Molyneaux <example@example.com>
Date: Fri, 20 Nov 2015 22:36:40 +0000
References: <mailman.12.1392379204.22573.centos-announce@centos.org>
Content-Type: multipart/signed; micalg="pgp-sha1"; protocol="application/pgp-signature"; boundary="=-8OGUbXGGezXx/m8jI4KD"
X-Mailer: Evolution 3.18.1 (3.18.1-1.fc23) 
Mime-Version: 1.0
X-Evolution-Source: 1288220347.2934.3@delta6thc


--=-8OGUbXGGezXx/m8jI4KD
Content-Type: multipart/mixed; boundary="=-mYf3f7WAELY8BNRlFdYo"


--=-mYf3f7WAELY8BNRlFdYo
Content-Type: text/plain
Content-Transfer-Encoding: quoted-printable

Hello

--=-mYf3f7WAELY8BNRlFdYo
Content-Disposition: inline
Content-Description: Forwarded message =?UTF-8?Q?=E2=80=94?= CentOS-announce
 Digest, Vol 108, Issue 9
Content-Type: message/rfc822

Delivered-To: example@example.com
Received: by 10.227.0.129 with SMTP id 1csp102594wbb; Fri, 14 Feb 2014
 04:01:13 -0800 (PST)
Content-Type: multipart/mixed; boundary="===============0954800312=="
MIME-Version: 1.0
From: centos-announce-request@centos.org
Subject: CentOS-announce Digest, Vol 108, Issue 9
To: centos-announce@centos.org
Reply-To: centos-announce@centos.org
Date: Fri, 14 Feb 2014 12:00:04 +0000
Message-ID: <mailman.12.1392379204.22573.centos-announce@centos.org>
X-BeenThere: centos-announce@centos.org
X-Mailman-Version: 2.1.9
Precedence: list
List-Id: "CentOS announcements \(security and general\) will be posted to
 this list." <centos-announce.centos.org>
List-Unsubscribe:
 <http://lists.centos.org/mailman/listinfo/centos-announce>,
 <mailto:centos-announce-request@centos.org?subject=unsubscribe>
List-Archive: <http://lists.centos.org/pipermail/centos-announce>
List-Post: <mailto:centos-announce@centos.org>
List-Help: <mailto:centos-announce-request@centos.org?subject=help>
List-Subscribe: <http://lists.centos.org/mailman/listinfo/centos-announce>,
 <mailto:centos-announce-request@centos.org?subject=subscribe>
Sender: centos-announce-bounces@centos.org
Errors-To: centos-announce-bounces@centos.org


--===============0954800312==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Description: CentOS-announce Digest, Vol 108, Issue 9
Content-Transfer-Encoding: quoted-printable

Send CentOS-announce mailing list submissions to
        centos-announce@centos.org

To subscribe or unsubscribe via the World Wide Web, visit
        http://lists.centos.org/mailman/listinfo/centos-announce
or, via email, send a message with subject or body 'help' to
        centos-announce-request@centos.org

You can reach the person managing the list at
        centos-announce-owner@centos.org

When replying, please edit your Subject line so it is more specific
than "Re: Contents of CentOS-announce digest..."
=0D
--===============0954800312==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Description: Today's Topics (6 messages)
Content-Transfer-Encoding: quoted-printable

Today's Topics:

   1. CESA-2014:0163 Important CentOS 5 kvm Update (Johnny Hughes)
   2. CESA-2014:0164 Moderate CentOS 6 mysql Update (Johnny Hughes)
   3. CEEA-2014:0165  CentOS 5 kdelibs Update (Johnny Hughes)
   4. CESA-2014:0175 Important CentOS 6 piranha Update (Johnny Hughes)
   5. CESA-2014:0174 Important CentOS 5 piranha Update (Johnny Hughes)
   6. CentOS at Scale 12x (Johnny Hughes)
=0D
--===============0954800312==
Content-Type: multipart/digest; boundary="===============1423313159=="
MIME-Version: 1.0


--===============1423313159==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Wed, 12 Feb 2014 19:33:17 +0000
Reply-To: centos@centos.org
Message-ID: <20140212193317.GA28103@chakra.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CESA-2014:0163 Important CentOS 5 kvm Update
Message: 1
Content-Transfer-Encoding: quoted-printable


CentOS Errata and Security Advisory 2014:0163 Important

Upstream details at : https://rhn.redhat.com/errata/RHSA-2014-0163.html

The following updated files have been uploaded and are currently=20
syncing to the mirrors: ( sha256sum Filename )=20


x86_64:
1d288a530ed89adada97ed8979e5f129848a4051ad16481edcaf7befdb8a3838  kmod-kvm-=
83-266.el5.centos.1.x86_64.rpm
3e80eaa38d2a7132193023018122f8b93bdd87eecde7b5e2e4ac7e98ebf01a2b  kmod-kvm-=
debug-83-266.el5.centos.1.x86_64.rpm
19ab38c1f03a8e931582250ad4ad40a7a439b74deae2b9c13af99fa11b794aa0  kvm-83-26=
6.el5.centos.1.x86_64.rpm
ab2e5b49a4e9a6fba2f1b19f6348793147bad0d504351866d557ab2d75b9c9f8  kvm-qemu-=
img-83-266.el5.centos.1.x86_64.rpm
1ab605f9bd17ba9a61a421f6132bea55873cd98573461b71e03f3b4713df98ef  kvm-tools=
-83-266.el5.centos.1.x86_64.rpm

Source:
a3d2506a7e8b2055a99acad6b19eb65da556d0dc8b87f4b8c183c2883c972149  kvm-83-26=
6.el5.centos.1.src.rpm



--=20
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net


=0D
--===============1423313159==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Wed, 12 Feb 2014 19:48:34 +0000
Reply-To: centos@centos.org
Message-ID: <20140212194834.GA28170@n04.lon1.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CESA-2014:0164 Moderate CentOS 6 mysql Update
Message: 2
Content-Transfer-Encoding: quoted-printable


CentOS Errata and Security Advisory 2014:0164 Moderate

Upstream details at : https://rhn.redhat.com/errata/RHSA-2014-0164.html

The following updated files have been uploaded and are currently=20
syncing to the mirrors: ( sha256sum Filename )=20

i386:
5d6f7adf4447f82150918dcf44cba6dedbdc327d44472c4abc88cc5460367dd8  mysql-5.1=
.73-3.el6_5.i686.rpm
8b9c123dea1c781a9a568ba4e5580191b55bc9e67be330acc0c296fd6e77a730  mysql-ben=
ch-5.1.73-3.el6_5.i686.rpm
505ddde78c99e2627ca79b5de754089cf6eb896258d90b67480ed6de0f017a7a  mysql-dev=
el-5.1.73-3.el6_5.i686.rpm
7d3c9182f5768824bdce6b3ef78509f6abb8df8dfe04ae60b9183679de3f3e6b  mysql-emb=
edded-5.1.73-3.el6_5.i686.rpm
3dc30e192d66ea39186dc156736feca34feff092ecdad0d5e0e2c09ca0fb051d  mysql-emb=
edded-devel-5.1.73-3.el6_5.i686.rpm
771ce477aeee96d7bb09e4bfe69fea1dc19d05d0836d30c9fe2d8e9a8f627cc7  mysql-lib=
s-5.1.73-3.el6_5.i686.rpm
6fb982c618a977e2b91b0ab01f576762d980a8dfd715366888d48f711144cd46  mysql-ser=
ver-5.1.73-3.el6_5.i686.rpm
d7ba139d4159d7110fd5ee742d3362382aa9861dcacb70fedde4c5bd76a6d69e  mysql-tes=
t-5.1.73-3.el6_5.i686.rpm

x86_64:
d2270a13c54e1bb437abd21c52ff31ce3e8ea52371caee115ac695c0a154d563  mysql-5.1=
.73-3.el6_5.x86_64.rpm
01eff9e169e46c4a61783c63a24e812dadd2de5ff53ae17c06f7e9a6b4d1ee4a  mysql-ben=
ch-5.1.73-3.el6_5.x86_64.rpm
505ddde78c99e2627ca79b5de754089cf6eb896258d90b67480ed6de0f017a7a  mysql-dev=
el-5.1.73-3.el6_5.i686.rpm
234377c2b83ad539bd4a70af47abaf2b6e8cd3467a59fd6d24808d1da88f4ad1  mysql-dev=
el-5.1.73-3.el6_5.x86_64.rpm
7d3c9182f5768824bdce6b3ef78509f6abb8df8dfe04ae60b9183679de3f3e6b  mysql-emb=
edded-5.1.73-3.el6_5.i686.rpm
3be25b9328385f0ab22f7fc86da0bf240a5317f77841eca66809fea2fd23e03d  mysql-emb=
edded-5.1.73-3.el6_5.x86_64.rpm
3dc30e192d66ea39186dc156736feca34feff092ecdad0d5e0e2c09ca0fb051d  mysql-emb=
edded-devel-5.1.73-3.el6_5.i686.rpm
52f7f372730c29c5531577d937d9f3d4008a09079091d52afee0894055f4504f  mysql-emb=
edded-devel-5.1.73-3.el6_5.x86_64.rpm
771ce477aeee96d7bb09e4bfe69fea1dc19d05d0836d30c9fe2d8e9a8f627cc7  mysql-lib=
s-5.1.73-3.el6_5.i686.rpm
ae6801e7cada3f97307d85cbd7e80dd996bc2460dc58932d1c8c3f0124b04e85  mysql-lib=
s-5.1.73-3.el6_5.x86_64.rpm
5ec01f451863b047918668c5334f94531769eb33b87d1cc5820f6cce9e77ef97  mysql-ser=
ver-5.1.73-3.el6_5.x86_64.rpm
07b2d0d9218da171bbfbdb909b15cc8eaa21b1a159d0e4f6c77034f9f087a8f9  mysql-tes=
t-5.1.73-3.el6_5.x86_64.rpm

Source:
e8f5b352bf4f89affedcd643442e3498a4c5c3fedfad73917905b6e9d5fead04  mysql-5.1=
.73-3.el6_5.src.rpm



--=20
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net


=0D
--===============1423313159==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Thu, 13 Feb 2014 16:52:55 +0000
Reply-To: centos@centos.org
Message-ID: <20140213165255.GA22586@chakra.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CEEA-2014:0165  CentOS 5 kdelibs Update
Message: 3
Content-Transfer-Encoding: quoted-printable


CentOS Errata and Enhancement Advisory 2014:0165=20

Upstream details at : https://rhn.redhat.com/errata/RHEA-2014-0165.html

The following updated files have been uploaded and are currently=20
syncing to the mirrors: ( sha256sum Filename )=20

i386:
03c0c18ec6538eb035bb80e5ac0acd9ace7e0b4007025e00351cf83655ef201d  kdelibs-3=
.5.4-29.el5.centos.i386.rpm
df066a23a2f2f7180f7f5f5d51e9eded293a14a513a6c707b68ef50a409b71e0  kdelibs-a=
pidocs-3.5.4-29.el5.centos.i386.rpm
8328f31c793c3c797fec026576d5052b3db78b7d24a89f4f412546761a343e0c  kdelibs-d=
evel-3.5.4-29.el5.centos.i386.rpm

x86_64:
03c0c18ec6538eb035bb80e5ac0acd9ace7e0b4007025e00351cf83655ef201d  kdelibs-3=
.5.4-29.el5.centos.i386.rpm
1222400236af581fec934fc0f17b9d2fc9fe8448806f325c6cec9fb6018ab114  kdelibs-3=
.5.4-29.el5.centos.x86_64.rpm
5814db3fa705456ff2f0a39109c77ad56aed26fb761320d5ee5c4e3f4a318bad  kdelibs-a=
pidocs-3.5.4-29.el5.centos.x86_64.rpm
8328f31c793c3c797fec026576d5052b3db78b7d24a89f4f412546761a343e0c  kdelibs-d=
evel-3.5.4-29.el5.centos.i386.rpm
86df9f000a39f6b310580996502b4e2792b174adcb1c9f2a72f6158ed649e7f1  kdelibs-d=
evel-3.5.4-29.el5.centos.x86_64.rpm

Source:
4a617d61320c1abc3de9e44e786ba8e6dc6c19e5cc49d2ce92bbd63d0339dd3d  kdelibs-3=
.5.4-29.el5.centos.src.rpm



--=20
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net


=0D
--===============1423313159==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Thu, 13 Feb 2014 20:05:42 +0000
Reply-To: centos@centos.org
Message-ID: <20140213200542.GA46343@n04.lon1.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CESA-2014:0175 Important CentOS 6 piranha Update
Message: 4
Content-Transfer-Encoding: quoted-printable


CentOS Errata and Security Advisory 2014:0175 Important

Upstream details at : https://rhn.redhat.com/errata/RHSA-2014-0175.html

The following updated files have been uploaded and are currently=20
syncing to the mirrors: ( sha256sum Filename )=20

i386:
4d4241930e9d10070344dbb6d9883796f53e34614cb8a0fb105aa75f8c5095be  piranha-0=
.8.6-4.el6_5.2.i686.rpm

x86_64:
1fbd986c4b4f2aef9f7294bbcaf82f6eabfad8f0819d1201dfe131ae63aa680b  piranha-0=
.8.6-4.el6_5.2.x86_64.rpm

Source:
f17264a1495ab17d935f0e272c2206fc53474e2bc302e88441da6d4dde38cf60  piranha-0=
.8.6-4.el6_5.2.src.rpm



--=20
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net


=0D
--===============1423313159==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Thu, 13 Feb 2014 20:20:56 +0000
Reply-To: centos@centos.org
Message-ID: <20140213202056.GA778@chakra.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CESA-2014:0174 Important CentOS 5 piranha Update
Message: 5
Content-Transfer-Encoding: quoted-printable


CentOS Errata and Security Advisory 2014:0174 Important

Upstream details at : https://rhn.redhat.com/errata/RHSA-2014-0174.html

The following updated files have been uploaded and are currently=20
syncing to the mirrors: ( sha256sum Filename )=20

i386:
cf98137c77e69d87b14092c435f50fde5bfc1576eb8daa7ea4bdc6a9fc7d30db  piranha-0=
.8.4-26.el5_10.1.i386.rpm

x86_64:
cf56574753c2eaf7ea586da76332094da6524c9cb165fbe4ce110c7699d23fdb  piranha-0=
.8.4-26.el5_10.1.x86_64.rpm

Source:
2ca2c83fda1a19014d171ace62f5e856afca2853fb7b7f2098859cd17e6f22ed  piranha-0=
.8.4-26.el5_10.1.src.rpm



--=20
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net


=0D
--===============1423313159==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: CentOS-Announce <centos-announce@centos.org>
Date: Thu, 13 Feb 2014 14:42:39 -0600
Reply-To: centos@centos.org
Message-ID: <52FD2E3F.7040603@centos.org>
Content-Type: multipart/signed; micalg=pgp-sha1; protocol="application/pgp-signature"; boundary="AvGQ06Sm2IBgNpfTV5qpg9tKusc5IJtD9"
Subject: [CentOS-announce] CentOS at Scale 12x
Message: 6

This is an OpenPGP/MIME signed message (RFC 4880 and 3156)
--AvGQ06Sm2IBgNpfTV5qpg9tKusc5IJtD9
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: quoted-printable

Several members of the CentOS team will be at Scale 12x
(http://bit.ly/1hEH6t5) in Los Angeles, California on February 21st to
23nd, 2014.

CentOS will be part of the "Infrastructure.Next at Scale" event (
http://bit.ly/1irKWUm ) event that happens on Friday (21st), and we will
have the following talk there:
http://bit.ly/1g2voUB

We will be at the Red Hat Community booth/table on both Saturday and
Sunday (22nd and 23rd) with free swag (teeshirts, stickers, etc).

We will have a Birds of a Feather session, details of which will be
provided at the table/booth when finalized.

Finally, we will also have a talk titled "CentOS Project Q&A Forum"
(http://bit.ly/1bQ5rVS) on Sunday (23rd).

If you are in the Los Angeles area, please stop by and see us at Scale
12x !!!

Thanks,
Johnny Hughes


--AvGQ06Sm2IBgNpfTV5qpg9tKusc5IJtD9
Content-Type: application/pgp-signature; name="signature.asc"
Content-Description: OpenPGP digital signature
Content-Disposition: attachment; filename="signature.asc"

-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.0.14 (GNU/Linux)

iEYEARECAAYFAlL9LkcACgkQTKkMgmrBY7NDAgCeJicd6G/WLvulJvuYxdwPQUG8
FCcAn30+5yjvFItIlaikVElS2RIces9w
=KsAo
-----END PGP SIGNATURE-----

--AvGQ06Sm2IBgNpfTV5qpg9tKusc5IJtD9--


--===============1423313159==--

--===============0954800312==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Description: Digest Footer
Content-Transfer-Encoding: quoted-printable

_______________________________________________
CentOS-announce mailing list
CentOS-announce@centos.org
http://lists.centos.org/mailman/listinfo/centos-announce
=0D
--===============0954800312==--

--=-mYf3f7WAELY8BNRlFdYo--

--=-8OGUbXGGezXx/m8jI4KD
Content-Type: application/pgp-signature; name="signature.asc"
Content-Description: This is a digitally signed message part
Content-Transfer-Encoding: 7bit

-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1

iQIcBAABAgAGBQJWT6B4AAoJEGOZTA5ZoLxX6UYP/1tzoRfT2TdbIoy6lt40RkWN
JEvWjwUQvwcL2YKt0GC7yTrfmZB1yhMMLNEqEBw9YOWXV+8w68PdfF+CBpqSGGcv
v1wABP6RSOl6MSWL+iLo21XdgxxyfyJQ5lAYjIdVmhaU8On4Os7ki0fYcsspaR0Y
YPLusNjJShqsJOkASfcWWH1DwwjdJ7MoDSVQEeDjFEJ98/B1auG3DnkwJ34rKQDE
YjzYyghKY5INuM0yAPs4cGf0wf3Z6Bn6kJS5J/S4smb6S4vuxIWKXLZ8sEST4pJP
Aku7VU3hm+UHlbW4jTPUMYE7DGtp8az4OrsEPf9y41qXazMi4+om3iqqeW1bmtGM
lDSkevCuJSwedyVUP/XGvDEiPrZTMTOwqHzq+Q+sjI7Ilt4rH/RoO3yt4X2BE60M
mUGUdCQLmuPgAtQ9ri7OMvZVKUWNCtoOIjKHyszMtOxJdhgAdBHWCJ8hQ3klnyeu
y9WftdEBUhJtfoNHyvc5ogd4h9C2ZbHeswPii3Zcl15R5jWZBflnzp62zizVMgx3
SyH52K7PD3YrSUJhxCkpbndOqxlKOyoxcDCBeWX1xgBf+AbRK+6HGD/e2Cf4HS1s
PYMhw44/d6IWZFBJl931k7sLB/ZCr7mklebGivwPY5LDa5V7eGE2glZlwxvsFE+l
s+PN63nlOtiyy8KEqWnI
=U4dH
-----END PGP SIGNATURE-----

--=-8OGUbXGGezXx/m8jI4KD--

"""
