##
#    Copyright (C) 2015-2016, 2018 Jessica Tallon & Matt Molyneaux
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

import os
import subprocess

from django_assets import Bundle, register
from webassets.exceptions import FilterError
from webassets.filter import get_filter
from webassets.filter.node_sass import NodeSass


class Sass(NodeSass):
    def _apply_sass(self, _in, out, cd=None):
        # Taken from WebAssets d1f3455e383446ca4ab0c644f326ee937e68e809
        # Copyright (c) 2008, Michael Elsdörfer <http://elsdoerfer.name>
        # All rights reserved.
        #
        # Redistribution and use in source and binary forms, with or without
        # modification, are permitted provided that the following conditions
        # are met:
        #
        #     1. Redistributions of source code must retain the above copyright
        #        notice, this list of conditions and the following disclaimer.
        #
        #     2. Redistributions in binary form must reproduce the above
        #        copyright notice, this list of conditions and the following
        #        disclaimer in the documentation and/or other materials
        #        provided with the distribution.
        #
        # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
        # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
        # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
        # FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
        # COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
        # INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
        # BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
        # LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
        # CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
        # LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
        # ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
        # POSSIBILITY OF SUCH DAMAGE.

        # Switch to source file directory if asked, so that this directory
        # is by default on the load path. We could pass it via --include-paths, but then
        # files in the (undefined) wd could shadow the correct files.
        old_dir = os.getcwd()
        if cd:
            os.chdir(cd)

        try:
            args = [self.binary or 'sass',
                    '--style', self.style or 'expanded',
                    '--stdin']

            if not self.use_scss:
                args.append("--indented")
            else:
                args.append("--no-indented")

            if (self.ctx.environment.debug if self.debug_info is None else self.debug_info):
                args.append('--trace')
            for path in self.load_paths or []:
                args.extend(['--load-path', path])

            if (self.cli_args):
                args.extend(self.cli_args)

            proc = subprocess.Popen(args,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    # shell: necessary on windows to execute
                                    # ruby files, but doesn't work on linux.
                                    shell=(os.name == 'nt'))
            stdout, stderr = proc.communicate(_in.read().encode('utf-8'))

            if proc.returncode != 0:
                raise FilterError(('sass: subprocess had error: stderr=%s, ' +
                                   'stdout=%s, returncode=%s') % (
                                                stderr, stdout, proc.returncode))
            elif stderr:
                print("node-sass filter has warnings:", stderr)

            out.write(stdout.decode('utf-8'))
        finally:
            if cd:
                os.chdir(old_dir)


thirdparty_path = os.path.join(os.getcwd(), "node_modules")
sass = get_filter(Sass, binary=os.path.join(thirdparty_path, ".bin", "sass"), scss=True, style="compressed",
                  load_paths=("./css", thirdparty_path))


uglify_args = ["--comments", "/^!/", "-m", "-c"]
uglify = get_filter("uglifyjs", binary=os.path.join(thirdparty_path, ".bin", "uglifyjs"), extra_args=uglify_args)


css = Bundle(
    "css/inboxen.scss",
    filters=(sass,),
    output="compiled/css/website.%(version)s.css",
)
register("inboxen_css", css)


js = Bundle(
    "thirdparty/jquery/dist/jquery.js",
    "js/utils.js",
    "js/copy.js",
    "js/alert.js",
    "js/home.js",
    "js/search.js",
    "js/inbox.js",
    filters=(uglify,),
    output="compiled/js/website.%(version)s.js",
)
register("inboxen_js", js)


chart_js = Bundle(
    "thirdparty/chart.js/dist/Chart.js",
    "js/stats.js",
    filters=(uglify,),
    output="compiled/js/stats.%(version)s.js",
)
register("chart_js", chart_js)
