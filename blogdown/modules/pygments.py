# -*- coding: utf-8 -*-
"""
    blogdown.modules.pygments
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds support for pygments.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from blogdown.signals import before_file_processed, \
     before_build_finished

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


html_formatter = None


def get_formatter_options(options):
    linenos = ('linenos' in options or
               'lineno-start' in options or
               'lineno-step' in options)
    return {
        'linenos': 1 if linenos else 0,
        'linenostart': options.get('lineno-start', 1),
        'linenostep': options.get('lineno-step', 1),
    }


def format_code(directive, formatter, code):
    try:
        lexer = get_lexer_by_name(directive.arguments[0])
    except ValueError:
        lexer = TextLexer()
    for k, v in get_formatter_options(directive.options).items():
        setattr(formatter, k, v)
    formatted = highlight(code, lexer, formatter)
    return [nodes.raw('', formatted, format='html')]


class CodeBlock(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'linenos': directives.flag,
        'lineno-start': int,
        'lineno-step': directives.positive_int,
    }

    def run(self):
        code = u'\n'.join(self.content)
        return format_code(self, html_formatter, code)


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
    before_file_processed.connect(inject_stylesheet)
    before_build_finished.connect(write_stylesheet)
