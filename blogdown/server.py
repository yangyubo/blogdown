# -*- coding: utf-8 -*-
"""
    blogdown.server
    ~~~~~~~~~~~~~~~

    Development server that rebuilds automatically

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
import sys
import posixpath
import urllib.parse

from http.server import HTTPServer, SimpleHTTPRequestHandler


class SimpleRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.server.builder.anything_needs_build():
            print('Detected change, building', file=sys.stderr)
            self.server.builder.run()
        SimpleHTTPRequestHandler.do_GET(self)

    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.server.builder.default_output_folder
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path

    def log_request(self, code='-', size='-'):
        pass

    def log_error(self, *args):
        pass

    def log_message(self, format, *args):
        pass


class Server(HTTPServer):

    def __init__(self, host, port, builder):
        HTTPServer.__init__(self, (host, int(port)), SimpleRequestHandler)
        self.builder = builder
