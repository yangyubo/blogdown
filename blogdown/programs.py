# -*- coding: utf-8 -*-
"""
    blogdown.programs
    ~~~~~~~~~~~~~~~~~

    Builtin build programs.

    :copyright: (c) 2010 by Armin Ronacher.
                (c) 2012 by Brant Young.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement
import os
import yaml
import shutil
from datetime import datetime
from StringIO import StringIO
from weakref import ref
from jinja2 import Markup

class Program(object):

    def __init__(self, context):
        self._context = ref(context)

    @property
    def context(self):
        rv = self._context()
        if rv is None:
            raise RuntimeError('context went away, program is invalid')
        return rv

    def get_desired_filename(self):
        folder, basename = os.path.split(self.context.source_filename)
        simple_name = os.path.splitext(basename)[0]
        if simple_name == 'index':
            suffix = 'index.html'
        else:
            suffix = os.path.join(simple_name, 'index.html')
        return os.path.join(folder, suffix)

    def prepare(self):
        pass

    def render_contents(self):
        return u''

    def run(self):
        raise NotImplementedError()


class CopyProgram(Program):
    """A program that copies a file over unchanged"""

    def run(self):
        self.context.make_destination_folder()
        shutil.copy(self.context.full_source_filename,
                    self.context.full_destination_filename)

    def get_desired_filename(self):
        return self.context.source_filename


class TemplatedProgram(Program):
    default_template = None

    def get_template_context(self):
        return {}

    def run(self):
        template_name = self.context.config.get('template') \
            or self.default_template
        context = self.get_template_context()
        rv = self.context.render_template(template_name, context)
        with self.context.open_destination_file() as f:
            f.write(rv.encode('utf-8') + '\n')


class RSTProgram(TemplatedProgram):
    """A program that renders an rst file into a template"""
    default_template = 'rst_display.html'
    _fragment_cache = None

    def prepare(self):
        headers = [u'---']
        with self.context.open_source_file() as f:
            for line in f:
                line = line.rstrip()
                if not line:
                    break
                headers.append(line)
            title = self.parse_text_title(f)

        cfg = yaml.load(StringIO(u'\n'.join(headers)))
        if cfg:
            if not isinstance(cfg, dict):
                raise ValueError('expected dict config in file "%s", got: %.40r' \
                    % (self.context.source_filename, cfg))
            self.context.config = self.context.config.add_from_dict(cfg)
            self.context.destination_filename = cfg.get(
                'destination_filename',
                self.context.destination_filename)

            title_override = cfg.get('title')
            if title_override is not None:
                title = title_override

            pub_date_override = cfg.get('pub_date')
            if pub_date_override is not None:
                if not isinstance(pub_date_override, datetime):
                    pub_date_override = datetime(pub_date_override.year,
                                                 pub_date_override.month,
                                                 pub_date_override.day)
                self.context.pub_date = pub_date_override

            summary_override = cfg.get('summary')
            if summary_override is not None:
                self.context.summary = summary_override

        if title is not None:
            self.context.title = title

    def parse_text_title(self, f):
        buffer = []
        for line in f:
            line = line.rstrip()
            if not line:
                break
            buffer.append(line)
        return self.render_rst('\n'.join(buffer).decode('utf-8')).get('title')

    def get_fragments(self):
        if self._fragment_cache is not None:
            return self._fragment_cache
        with self.context.open_source_file() as f:
            while f.readline().strip():
                pass
            rv = self.render_rst(f.read().decode('utf-8'))
        self._fragment_cache = rv
        return rv

    def render_rst(self, contents):
        from docutils.core import publish_parts

        settings = {
            'initial_header_level': self.context.config.get('rst_header_level', 2),
            'rstblog_context':      self.context
        }
        parts = publish_parts(source=contents,
                              writer_name='html4css1',
                              settings_overrides=settings)
        return {
            'title':        Markup(parts['title']).striptags(),
            'html_title':   Markup(parts['html_title']),
            'fragment':     Markup(parts['fragment'])
        }

    def render(self, contents):
        if not contents:
            return u''
        return self.render_rst(contents)['fragment']

    def render_contents(self):
        return self.get_fragments()['fragment']

    def get_template_context(self):
        ctx = TemplatedProgram.get_template_context(self)
        ctx['rst'] = self.get_fragments()
        return ctx

class MDProgram(TemplatedProgram):
    """A program that renders an rst file into a template"""
    default_template = 'md_display.html'

    def __init__(self, context):
        from markdown import Markdown
        self.md = Markdown(
            output_format     = 'html5',
            safe_mode         = 'escape',
            enable_attributes = True,
            extensions        = [
                'smart_strong',
                'fenced_code',
                'footnotes',
                'attr_list',
                'def_list',
                'tables',
                'abbr',
                'meta',
                'headerid'
            ]
        )

        self.contents = {}

        TemplatedProgram.__init__(self, context)

    def prepare(self):
        with self.context.open_source_file() as f:
            parsed = self.md.convert(f.read().decode('utf-8'))

        self.context.config = self.context.config.add_from_dict(self.md.Meta)
        self.contents['fragment'] = parsed
        self.contents['html_title'] = self.contents['title'] = self.context.title = u' '.join(self.md.Meta.get('title', u''))
        self.contents['summary'] = self.context.summary = u' '.join(self.md.Meta.get('summary', u''))

    def render(self, contents):
        self.md.reset()
        return self.md.convert(contents)

    def render_contents(self):
        return self.contents['fragment']

    def get_template_context(self):
        ctx = TemplatedProgram.get_template_context(self)
        ctx['md'] = self.contents
        return ctx
