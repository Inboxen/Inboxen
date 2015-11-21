# -*- coding: utf-8 -*-
##
#    Copyright (C) 2014-2015 Jessica Tallon & Matt Molyneaux
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

from django import test
from django.core import urlresolvers
from salmon import mail

from inboxen import models
from inboxen.tests import factories
from inboxen.utils.email import _unicode_damnit
from router.app.helpers import make_email


BODY = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<style type="text/css">
p {color: #ffffff;}
</style>
</head>
<body>
<p>Hello! This is a test of <img src="http://example.com/coolface.jpg"></p>
<p>&nbsp;</p>
<p>£££</p><p><a href="http://example.com/?q=thing">link</a></p>
</body>
</html>
"""


METALESS_BODY = """<html>
<head>
<style type="text/css">
p {color: #ffffff;}
</style>
</head>
<body>
<p>Hello! This is a test of <img src="http://example.com/coolface.jpg"></p>
<p>&nbsp;</p>
<p>$$$</p><p><a href="http://example.com/?q=thing">link</a></p>
</body>
</html>
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


class EmailViewTestCase(test.TestCase):
    def setUp(self):
        super(EmailViewTestCase, self).setUp()

        self.user = factories.UserFactory()
        self.email = factories.EmailFactory(inbox__user=self.user)
        body = factories.BodyFactory(data=BODY)
        part = factories.PartListFactory(email=self.email, body=body)
        factories.HeaderFactory(part=part, name="From")
        factories.HeaderFactory(part=part, name="Subject")
        factories.HeaderFactory(part=part, name="Content-Type", data="text/html; charset=\"utf-8\"")

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        kwargs = {
            "inbox": self.email.inbox.inbox,
            "domain": self.email.inbox.domain.domain,
            "id": self.email.eid,
        }
        return urlresolvers.reverse("email-view", kwargs=kwargs)

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        # check that delete button has correct value
        button = "value=\"%s\" name=\"delete-single\""
        button = button % self.email.eid
        self.assertIn(button, response.content)

        # check for no-referrer
        self.assertIn('<meta name="referrer" content="no-referrer">', response.content)

    def test_get_with_headers(self):
        response = self.client.get(self.get_url() + "?all-headers=1")
        self.assertEqual(response.status_code, 200)

        headersfetchall = response.context["headersfetchall"]
        self.assertTrue(headersfetchall)

        response = self.client.get(self.get_url() + "?all-headers=0")
        self.assertEqual(response.status_code, 200)

        headersfetchall = response.context["headersfetchall"]
        self.assertFalse(headersfetchall)

    def test_body_encoding_with_imgDisplay(self):
        response = self.client.get(self.get_url() + "?imgDisplay=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertIn(u"http://example.com/coolface.jpg", content)
        self.assertNotIn(u"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_body_encoding_without_imgDisplay(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertNotIn(u"http://example.com/coolface.jpg", content)
        self.assertIn(u"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_attachments_get(self):
        part = self.email.parts.get()
        url = urlresolvers.reverse("email-attachment", kwargs={"method": "download", "attachmentid": part.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        important = self.email.flags.important

        params = {"important-toggle": ""}
        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "http://testserver%s" % self.get_url())
        email = models.Email.objects.get(pk=self.email.pk)
        self.assertNotEqual(email.flags.important, important)

        important = not important
        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "http://testserver%s" % self.get_url())
        email = models.Email.objects.get(pk=self.email.pk)
        self.assertNotEqual(email.flags.important, important)

    def test_html_a(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u'<a href="/click/?url=http%3A//example.com/%3Fq%3Dthing" target="_blank">link</a>', content)

    # TODO: test body choosing with multipart emails


class BadEmailTestCase(test.TestCase):
    def setUp(self):
        super(BadEmailTestCase, self).setUp()

        self.user = factories.UserFactory()
        self.email = factories.EmailFactory(inbox__user=self.user)
        body = factories.BodyFactory(data=BODY)
        part = factories.PartListFactory(email=self.email, body=body)
        factories.HeaderFactory(part=part, name="From")
        factories.HeaderFactory(part=part, name="Subject")
        factories.HeaderFactory(part=part, name="Content-Type", data="text/html; charset=\"windows-1252\"")
        factories.HeaderFactory(part=part, name="Content-Disposition", data="inline filename=\"He\n\rl\rlo\n.jpg\"")

        self.email_metaless = factories.EmailFactory(inbox__user=self.user)
        body = factories.BodyFactory(data=METALESS_BODY)
        part = factories.PartListFactory(email=self.email_metaless, body=body)
        factories.HeaderFactory(part=part, name="From")
        factories.HeaderFactory(part=part, name="Subject")
        factories.HeaderFactory(part=part, name="Content-Type", data="text/html; charset=\"ascii\"")

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self, email=None):
        if email is None:
            email = self.email

        kwargs = {
            "inbox": email.inbox.inbox,
            "domain": email.inbox.domain.domain,
            "id": email.eid,
        }
        return urlresolvers.reverse("email-view", kwargs=kwargs)

    def test_body_encoding_with_imgDisplay(self):
        response = self.client.get(self.get_url() + "?imgDisplay=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertIn(u"http://example.com/coolface.jpg", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_body_encoding_without_imgDisplay(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertNotIn(u"http://example.com/coolface.jpg", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_body_with_no_meta(self):
        response = self.client.get(self.get_url(self.email_metaless) + "?imgDisplay=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>$$$</p>", content)
        self.assertIn(u"http://example.com/coolface.jpg", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_attachments_get(self):
        part = self.email.parts.get()
        url = urlresolvers.reverse("email-attachment", kwargs={"method": "download", "attachmentid": part.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("He l lo .jpg", response["Content-Disposition"])

    def test_html_a(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u'<a href="/click/?url=http%3A//example.com/%3Fq%3Dthing" target="_blank">link</a>', content)


class RealExamplesTestCase(test.TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.inbox = factories.InboxFactory(user=self.user)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        kwargs = {
            "inbox": self.email.inbox.inbox,
            "domain": self.email.inbox.domain.domain,
            "id": self.email.eid,
        }
        return urlresolvers.reverse("email-view", kwargs=kwargs)

    def test_digest(self):
        self.msg = mail.MailRequest("", "", "", EXAMPLE_DIGEST)
        make_email(self.msg, self.inbox)
        self.email = models.Email.objects.get()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        # this email should display all leaves
        leaf_part_count = len([i for i in self.email.get_parts() if i.is_leaf_node()])
        self.assertEqual(len(response.context["email"]["bodies"]), leaf_part_count)

    def test_signed_forwarded_digest(self):
        self.msg = mail.MailRequest("", "", "", EXAMPLE_SIGNED_FORWARDED_DIGEST)
        make_email(self.msg, self.inbox)
        self.email = models.Email.objects.get()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        leaf_part_count = len([i for i in self.email.get_parts() if i.is_leaf_node()])
        self.assertEqual(leaf_part_count, 12)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        self.assertEqual(response.context["email"]["bodies"][0], "<pre>Hello\n</pre>")

    def test_alterative(self):
        self.msg = mail.MailRequest("", "", "", EXAMPLE_ALT)
        make_email(self.msg, self.inbox)
        self.email = models.Email.objects.get()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)


class UtilityTestCase(test.TestCase):
    def test_is_unicode(self):
        string = "Hey there!"
        self.assertTrue(isinstance(_unicode_damnit(string), unicode))

    def test_unicode_passthrough(self):
        already_unicode = u"€"

        # if this doesn't passthrough, it will error
        _unicode_damnit(already_unicode, "ascii", "strict")
