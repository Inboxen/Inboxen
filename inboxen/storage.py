# Backported from Django 1.7
# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of Django nor the names of its contributors may be used
#        to endorse or promote products derived from this software without
#        specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import unicode_literals
import hashlib
import simplejson as json
import os
import posixpath
import re

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.encoding import force_bytes, force_text
from django.utils.six.moves.urllib.parse import unquote, urlsplit, urlunsplit, urldefrag

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.contrib.staticfiles.utils import matches_patterns

from inboxen.utils import generate_maintenance_page


class HashedFilesMixin(object):
    default_template = """url("%s")"""
    patterns = (
        ("*.css", (
            r"""(url\(['"]{0,1}\s*(.*?)["']{0,1}\))""",
            (r"""(@import\s*["']\s*(.*?)["'])""", """@import url("%s")"""),
        )),
    )

    def __init__(self, *args, **kwargs):
        super(HashedFilesMixin, self).__init__(*args, **kwargs)
        self._patterns = OrderedDict()
        self.hashed_files = {}
        for extension, patterns in self.patterns:
            for pattern in patterns:
                if isinstance(pattern, (tuple, list)):
                    pattern, template = pattern
                else:
                    template = self.default_template
                compiled = re.compile(pattern, re.IGNORECASE)
                self._patterns.setdefault(extension, []).append((compiled, template))

    def file_hash(self, name, content=None):
        """
        Retuns a hash of the file with the given name and optional content.
        """
        if content is None:
            return None
        md5 = hashlib.md5()
        for chunk in content.chunks():
            md5.update(chunk)
        return md5.hexdigest()[:12]

    def hashed_name(self, name, content=None):
        parsed_name = urlsplit(unquote(name))
        clean_name = parsed_name.path.strip()
        opened = False
        if content is None:
            if not self.exists(clean_name):
                raise ValueError("The file '%s' could not be found with %r." %
                                 (clean_name, self))
            try:
                content = self.open(clean_name)
            except IOError:
                # Handle directory paths and fragments
                return name
            opened = True
        try:
            file_hash = self.file_hash(clean_name, content)
        finally:
            if opened:
                content.close()
        path, filename = os.path.split(clean_name)
        root, ext = os.path.splitext(filename)
        if file_hash is not None:
            file_hash = ".%s" % file_hash
        hashed_name = os.path.join(path, "%s%s%s" %
                                   (root, file_hash, ext))
        unparsed_name = list(parsed_name)
        unparsed_name[2] = hashed_name
        # Special casing for a @font-face hack, like url(myfont.eot?#iefix")
        # http://www.fontspring.com/blog/the-new-bulletproof-font-face-syntax
        if '?#' in name and not unparsed_name[3]:
            unparsed_name[2] += '?'
        return urlunsplit(unparsed_name)

    def url(self, name, force=False):
        """
        Returns the real URL in DEBUG mode.
        """
        if settings.DEBUG and not force:
            hashed_name, fragment = name, ''
        else:
            clean_name, fragment = urldefrag(name)
            if urlsplit(clean_name).path.endswith('/'):  # don't hash paths
                hashed_name = name
            else:
                hashed_name = self.stored_name(clean_name)

        final_url = super(HashedFilesMixin, self).url(hashed_name)

        # Special casing for a @font-face hack, like url(myfont.eot?#iefix")
        # http://www.fontspring.com/blog/the-new-bulletproof-font-face-syntax
        query_fragment = '?#' in name  # [sic!]
        if fragment or query_fragment:
            urlparts = list(urlsplit(final_url))
            if fragment and not urlparts[4]:
                urlparts[4] = fragment
            if query_fragment and not urlparts[3]:
                urlparts[2] += '?'
            final_url = urlunsplit(urlparts)

        return unquote(final_url)

    def url_converter(self, name, template=None):
        """
        Returns the custom URL converter for the given file name.
        """
        if template is None:
            template = self.default_template

        def converter(matchobj):
            """
            Converts the matched URL depending on the parent level (`..`)
            and returns the normalized and hashed URL using the url method
            of the storage.
            """
            matched, url = matchobj.groups()
            # Completely ignore http(s) prefixed URLs,
            # fragments and data-uri URLs
            if url.startswith(('#', 'http:', 'https:', 'data:', '//')):
                return matched
            name_parts = name.split(os.sep)
            # Using posix normpath here to remove duplicates
            url = posixpath.normpath(url)
            url_parts = url.split('/')
            parent_level, sub_level = url.count('..'), url.count('/')
            if url.startswith('/'):
                sub_level -= 1
                url_parts = url_parts[1:]
            if parent_level or not url.startswith('/'):
                start, end = parent_level + 1, parent_level
            else:
                if sub_level:
                    if sub_level == 1:
                        parent_level -= 1
                    start, end = parent_level, 1
                else:
                    start, end = 1, sub_level - 1
            joined_result = '/'.join(name_parts[:-start] + url_parts[end:])
            hashed_url = self.url(unquote(joined_result), force=True)
            file_name = hashed_url.split('/')[-1:]
            relative_url = '/'.join(url.split('/')[:-1] + file_name)

            # Return the hashed version to the file
            return template % unquote(relative_url)

        return converter

    def post_process(self, paths, dry_run=False, **options):
        """
        Post process the given OrderedDict of files (called from collectstatic).

        Processing is actually two separate operations:

        1. renaming files to include a hash of their content for cache-busting,
           and copying those files to the target storage.
        2. adjusting files which contain references to other files so they
           refer to the cache-busting filenames.

        If either of these are performed on a file, then that file is considered
        post-processed.
        """
        # don't even dare to process the files if we're in dry run mode
        if dry_run:
            return

        # where to store the new paths
        hashed_files = OrderedDict()

        # build a list of adjustable files
        matches = lambda path: matches_patterns(path, self._patterns.keys())
        adjustable_paths = [path for path in paths if matches(path)]

        # then sort the files by the directory level
        path_level = lambda name: len(name.split(os.sep))
        for name in sorted(paths.keys(), key=path_level, reverse=True):

            # use the original, local file, not the copied-but-unprocessed
            # file, which might be somewhere far away, like S3
            storage, path = paths[name]
            with storage.open(path) as original_file:

                # generate the hash with the original content, even for
                # adjustable files.
                hashed_name = self.hashed_name(name, original_file)

                # then get the original's file content..
                if hasattr(original_file, 'seek'):
                    original_file.seek(0)

                hashed_file_exists = self.exists(hashed_name)
                processed = False

                # ..to apply each replacement pattern to the content
                if name in adjustable_paths:
                    content = original_file.read().decode(settings.FILE_CHARSET)
                    for patterns in self._patterns.values():
                        for pattern, template in patterns:
                            converter = self.url_converter(name, template)
                            try:
                                content = pattern.sub(converter, content)
                            except ValueError as exc:
                                yield name, None, exc
                    if hashed_file_exists:
                        self.delete(hashed_name)
                    # then save the processed result
                    content_file = ContentFile(force_bytes(content))
                    saved_name = self._save(hashed_name, content_file)
                    hashed_name = force_text(self.clean_name(saved_name))
                    processed = True
                else:
                    # or handle the case in which neither processing nor
                    # a change to the original file happened
                    if not hashed_file_exists:
                        processed = True
                        saved_name = self._save(hashed_name, original_file)
                        hashed_name = force_text(self.clean_name(saved_name))

                # and then set the cache accordingly
                hashed_files[self.hash_key(name)] = hashed_name
                yield name, hashed_name, processed

        # Finally store the processed paths
        self.hashed_files.update(hashed_files)

    def clean_name(self, name):
        return name.replace('\\', '/')

    def hash_key(self, name):
        return name

    def stored_name(self, name):
        hash_key = self.hash_key(name)
        cache_name = self.hashed_files.get(hash_key)
        if cache_name is None:
            cache_name = self.clean_name(self.hashed_name(name))
            # store the hashed name if there was a miss, e.g.
            # when the files are still processed
            self.hashed_files[hash_key] = cache_name
        return cache_name


class ManifestFilesMixin(HashedFilesMixin):
    manifest_version = '1.0'  # the manifest format standard
    manifest_name = 'staticfiles.json'

    def __init__(self, *args, **kwargs):
        super(ManifestFilesMixin, self).__init__(*args, **kwargs)
        self.hashed_files = self.load_manifest()

    def read_manifest(self):
        try:
            with self.open(self.manifest_name) as manifest:
                return manifest.read().decode('utf-8')
        except IOError:
            return None

    def load_manifest(self):
        content = self.read_manifest()
        if content is None:
            return OrderedDict()
        try:
            stored = json.loads(content, object_pairs_hook=OrderedDict)
        except ValueError:
            pass
        else:
            version = stored.get('version', None)
            if version == '1.0':
                return stored.get('paths', OrderedDict())
        raise ValueError("Couldn't load manifest '%s' (version %s)" %
                         (self.manifest_name, self.manifest_version))

    def post_process(self, *args, **kwargs):
        self.hashed_files = OrderedDict()
        all_post_processed = super(ManifestFilesMixin,
                                   self).post_process(*args, **kwargs)
        for post_processed in all_post_processed:
            yield post_processed
        self.save_manifest()

    def save_manifest(self):
        payload = {'paths': self.hashed_files, 'version': self.manifest_version}
        if self.exists(self.manifest_name):
            self.delete(self.manifest_name)
        contents = json.dumps(payload).encode('utf-8')
        self._save(self.manifest_name, ContentFile(contents))


class ManifestStaticFilesStorage(ManifestFilesMixin, StaticFilesStorage):
    """
    A static file system storage backend which also saves
    hashed copies of the files it saves.
    """
    def post_process(self, *args, **kwargs):
        all_post_processed = super(ManifestStaticFilesStorage,
                                   self).post_process(*args, **kwargs)
        for post_processed in all_post_processed:
            yield post_processed
        generate_maintenance_page()
