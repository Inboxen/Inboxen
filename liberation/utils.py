import binascii
import uu
from cStringIO import StringIO
from email import encoders
from email.message import Message


class EncodeMessage(Message):
    """Just like a normal email.message.Message, but it automatically enocdes body parts"""
    def get_payload(self, i=None):
        # taken from http://hg.python.org/cpython/file/0926adcc335c/Lib/email/message.py
        # Copyright (C) 2001-2006 Python Software Foundation
        # See PY-LIC for licence
        if i is None:
            payload = self._payload
        elif not isinstance(self._payload, list):
            raise TypeError('Expected list, got %s' % type(self._payload))
        else:
            payload = self._payload[i]

        if self.is_multipart():
            return payload
        cte = self.get('content-transfer-encoding', '').lower()
        if cte == 'quoted-printable':
            return encoders._qencode(payload)
        elif cte == 'base64':
            try:
                return encoders._bencode(payload)
            except binascii.Error:
                # Incorrect padding
                return payload
        elif cte in ('x-uuencode', 'uuencode', 'uue', 'x-uue'):
            sfp = StringIO()
            try:
                uu.encode(StringIO(payload + '\n'), sfp, quiet=True)
                payload = sfp.getvalue()
            except uu.Error:
                # Some decoding problem
                return payload
        # Everything else, including encodings with 8bit or 7bit are returned
        # unchanged.
        return payload


def make_message(message):
    """ Make a Python  email.message.Message from our models """
    parents = {}
    part_list = message.parts.all()
    first = None

    for part in part_list:
        msg = EncodeMessage()

        header_set = part.header_set.order_by("ordinal").select_related("name__name", "data__data")
        for header in header_set:
            msg[header.name.name] = header.data.data

        if part.is_leaf_node():
            msg.set_payload(str(part.body.data))
        else:
            parents[part.id] = msg

        if first is None:
            first = msg
        else:
            parents[part.parent_id].attach(msg)

    return first
