##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

from __future__ import print_function
import re
import sys

import psycopg2

"""
Postfix check_policy script

Requires the following view:

    CREATE VIEW postfix_view
    AS
      SELECT "inboxen_inbox"."inbox"   AS "inbox",
             "inboxen_domain"."domain" AS "domain"
      FROM   "inboxen_inbox"
             INNER JOIN "inboxen_domain"
                     ON ( "inboxen_inbox"."domain_id" = "inboxen_domain"."id" )
      WHERE  "inboxen_inbox"."flags" = ( "inboxen_inbox"."flags" & -2 );

It is recommended that you create a separate role that only has read access to
this view. This will reduce the security risk that this script poses.

Remember to add addresses that you still want to receive, but are not going to
Inboxen, to bypass_*
"""
bypass_local = ["root", "postmaster", "dns", "support"]
bypass_domain = []
bypass_address = []


line_matcher = re.compile(r"^([^=]+)=(.*)$")
address_matcher = re.compile(r"^([^@]+)@(.*)$")
query_template = "select 1 from postfix_view where inbox=%s and domain=%s"

reject = "action=REJECT {0}\n\n"
accept = "action=DUNNO {0}\n\n"

connection = psycopg2.connect("dbname=inboxen user=inboxen password=inboxen")
cursor = connection.cursor()

request = {}

# This should be refactored as a daemon
for line in sys.stdin:
    line = line[:-1]
    if line != "":
        match = line_matcher.match(line)
        request[match.group(1)] = match.group(2)
    elif len(request) > 0:
        if request["protocol_state"] != "RCPT":
            print(accept.format("Wrong state"))
            request = {}
            continue

        match = address_matcher.match(request["recipient"])
        args = match.group(1, 2)

        if (args[0] in bypass_local
                or args[1] in bypass_domain
                or request["recipient"] in bypass_address
                ):
            print(accept.format("Bypassed"))
            request = {}
            continue

        cursor.execute(query_template, args)
        try:
            result = cursor.fetchone()
        except psycopg2.ProgrammingError:
            result = None

        if result is None:
            print(reject.format("Not found"))
        else:
            print(accept.format("Result found"))

        request = {}
