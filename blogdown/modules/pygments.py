# -*- coding: utf-8 -*-
"""
    blogdown.modules.pygments
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds support for pygments.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os

from blogdown.signals import before_file_processed, \
     before_build_finished

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


html_formatter = None


def _range(start, stop=None):
    return range(int(start), int(start if stop is None else stop)+1)

def _parserange(expr):
    return list(_range(*expr.strip().split('-')))


def parselinenos(spec):
    """Parse a line number spec (such as "1,2,4-6") and return a list of
    wanted line numbers.
    """
    if spec is None:
        return list()
    try:
        return sum(map(_parserange, spec.split(',')), [])
    except (ValueError, TypeError):
        raise ValueError('invalid line number spec: %r' % spec)


def get_linenos(options):
    return ('linenos' in options or
            'lineno-start' in options or
            'lineno-step' in options)


def get_formatter_options(options):
    return {
        'linenos': 1 if get_linenos(options) else 0,
        'linenostart': options.get('lineno-start', 1),
        'linenostep': options.get('lineno-step', 1),
        'hl_lines': parselinenos(options.get('emphasize-lines')),
    }


def format_code(options, formatter, code, language):
    try:
        lexer = get_lexer_by_name(language)
    except ValueError:
        lexer = TextLexer()
    fmt_opt = get_formatter_options(options)
    for k, v in fmt_opt.items():
        setattr(formatter, k, v)
    formatted = highlight(code, lexer, formatter)
    literal_block = nodes.raw('', formatted, format='html')
    linenos = fmt_opt['linenos']
    caption = options.get('caption')
    classes = [
        'literal-block-wrapper',
        'with_linenos' if linenos else 'without_linenos',
        'with_caption' if caption else 'without_caption',
    ]
    container = nodes.container('', literal_block=True, classes=classes)
    if caption:
        container += nodes.caption(caption, '', nodes.Text(caption))
    container += literal_block
    return [container]


class CodeBlock(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'linenos': directives.flag,
        'lineno-start': int,
        'lineno-step': directives.positive_int,
        'caption': directives.unchanged_required,
        'emphasize-lines': directives.unchanged_required,
    }

    def run(self):
        language = self.arguments[0]
        code = u'\n'.join(self.content)
        return format_code(self.options, html_formatter, code, language)


class LiteralInclude(CodeBlock):

    option_spec = CodeBlock.option_spec.copy()
    option_spec.update({
        'caption': directives.unchanged,
        'language': directives.unchanged_required,
        'encoding': directives.encoding,
        'lines': directives.unchanged_required,
    })

    def read_file(self, filename, encoding):
        context = self.state.document.settings.rstblog_context
        dirname = os.path.dirname(context.full_source_filename)
        fullpath = os.path.join(dirname, filename)
        with io.open(fullpath, 'rt', encoding=encoding) as f:
            return list(f)

    def run(self):
        options = self.options.copy()
        language = options.get('language')
        encoding = options.get('encoding', 'utf-8')
        filename = self.arguments[0]
        lines = self.read_file(filename, encoding)
        cut = options.get('lines')
        if cut:
            start, stop = cut.split('-')
            start = int(start)-1 if start else None
            stop = int(stop) if stop else None
            lines = lines[start:stop]
            if get_linenos(options) and not options.get('lineno-start'):
                options['lineno-start'] = start
        if 'caption' in options and not options['caption']:
            options['caption'] = os.path.basename(filename)
        code = "".join(lines)
        return format_code(options, html_formatter, code, language)


def inject_stylesheet(context, **kwargs):
    context.add_stylesheet('_pygments.css')


def write_stylesheet(builder, **kwargs):
    with builder.open_static_file('_pygments.css', 'w') as f:
        f.write(html_formatter.get_style_defs())


def setup(builder):
    global html_formatter
    style = get_style_by_name(builder.config.root_get('modules.pygments.style'))
    html_formatter = HtmlFormatter(style=style, cssclass='hll')
    directives.register_directive('code-block', CodeBlock)
    directives.register_directive('sourcecode', CodeBlock)
    directives.register_directive('literalinclude', LiteralInclude)
    before_file_processed.connect(inject_stylesheet)
    before_build_finished.connect(write_stylesheet)
