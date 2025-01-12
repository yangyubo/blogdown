# -*- coding: utf-8 -*-
"""
    blogdown.programs
    ~~~~~~~~~~~~~~~~~

    Builtin build programs.

    :copyright: (c) 2010 by Armin Ronacher.
                (c) 2012 by Brant Young.
    :license: BSD, see LICENSE for more details.
"""
import os
import yaml
import shutil
from datetime import datetime
from weakref import ref
from markupsafe import Markup


class Program(object):
    def __init__(self, context):
        self._context = ref(context)

    @property
    def context(self):
        rv = self._context()
        if rv is None:
            raise RuntimeError("context went away, program is invalid")
        return rv

    def get_desired_filename(self):
        folder, basename = os.path.split(self.context.source_filename)
        simple_name = os.path.splitext(basename)[0]
        if simple_name == "index":
            suffix = "index.html"
        else:
            suffix = os.path.join(simple_name, "index.html")
        return os.path.join(folder, suffix)

    def prepare(self):
        pass

    def render_contents(self):
        return ""

    def run(self):
        raise NotImplementedError()


class CopyProgram(Program):
    """A program that copies a file over unchanged"""

    def run(self):
        self.context.make_destination_folder()
        shutil.copy(
            self.context.full_source_filename,
            self.context.full_destination_filename,
        )

    def get_desired_filename(self):
        return self.context.source_filename


class TemplatedProgram(Program):
    default_template = None

    def get_template_context(self):
        return {}

    def run(self):
        template_name = (
            self.context.config.get("template") or self.default_template
        )
        context = self.get_template_context()
        rv = self.context.render_template(template_name, context)
        with self.context.open_destination_file() as f:
            f.write(rv + "\n")


def iter_header_lines(lines):
    """
    Iterate lines in the header.

    If header starts with '---' it must also end with that. Otherwise it can
    end with a blank line or '---'.
    """
    line = next(lines)
    doc_sep = line == "---"
    if not doc_sep:
        yield line
    for line in lines:
        if line == "---" or (not doc_sep and not line):
            return
        yield line


def parse_header_lines(lines):
    """
    Extract header lines and return parsed as YAML.

    :param lines: should be an iterator or file-like object.
    """
    lines = iter_header_lines(line.rstrip("\n") for line in lines)
    return yaml.unsafe_load("\n".join(lines))


class RSTProgram(TemplatedProgram):
    """A program that renders an rst file into a template"""

    default_template = "rst_display.html"
    _fragment_cache = None

    def prepare(self):
        with self.context.open_source_file() as f:
            cfg = parse_header_lines(f)
            title = self.parse_text_title(f)

        if cfg:
            if not isinstance(cfg, dict):
                raise ValueError(
                    'expected dict config in file "%s", got: %.40r'
                    % (self.context.source_filename, cfg)
                )
            self.context.config = self.context.config.add_from_dict(cfg)
            self.context.destination_filename = cfg.get(
                "destination_filename", self.context.destination_filename
            )

            title_override = cfg.get("title")
            if title_override is not None:
                title = title_override

            pub_date_override = cfg.get("pub_date")
            if pub_date_override is not None:
                if not isinstance(pub_date_override, datetime):
                    pub_date_override = datetime(
                        pub_date_override.year,
                        pub_date_override.month,
                        pub_date_override.day,
                    )
                self.context.pub_date = pub_date_override

            summary_override = cfg.get("summary")
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
        return self.render_rst("\n".join(buffer)).get("title")

    def get_fragments(self):
        if self._fragment_cache is not None:
            return self._fragment_cache
        with self.context.open_source_file() as f:
            while f.readline().strip():
                pass
            rv = self.render_rst(f.read())
        self._fragment_cache = rv
        return rv

    def render_rst(self, contents):
        from docutils.core import publish_parts

        settings = {
            "initial_header_level": self.context.config.get(
                "rst_header_level", 2
            ),
            "rstblog_context": self.context,
        }
        parts = publish_parts(
            source=contents,
            writer_name="html4css1",
            settings_overrides=settings,
        )
        return {
            "title": Markup(parts["title"]).striptags(),
            "html_title": Markup(parts["html_title"]),
            "fragment": Markup(parts["fragment"]),
        }

    def render(self, contents):
        if not contents:
            return ""
        return self.render_rst(contents)["fragment"]

    def render_contents(self):
        return self.get_fragments()["fragment"]

    def get_template_context(self):
        ctx = TemplatedProgram.get_template_context(self)
        ctx["rst"] = self.get_fragments()
        return ctx


class MDProgram(TemplatedProgram):
    """A program that renders an rst file into a template"""

    default_template = "md_display.html"

    def __init__(self, context):
        from markdown import Markdown

        self.md = Markdown(
            output_format="html5",
            safe_mode="escape",
            enable_attributes=True,
            extensions=[
                "smart_strong",
                "fenced_code",
                "footnotes",
                "attr_list",
                "def_list",
                "tables",
                "abbr",
                "meta",
                "headerid",
                "codehilite(pygments_style=tango,"
                + "css_class=syntax,guess_lang=True)",
            ],
        )

        self.contents = {}

        TemplatedProgram.__init__(self, context)

    def prepare(self):
        with self.context.open_source_file() as f:
            parsed = self.md.convert(f.read())

        self.context.config = self.context.config.add_from_dict(self.md.Meta)
        self.contents["fragment"] = parsed
        self.contents["html_title"] = self.contents[
            "title"
        ] = self.context.title = " ".join(self.md.Meta.get("title", ""))
        self.contents["summary"] = self.context.summary = " ".join(
            self.md.Meta.get("summary", "")
        )

    def render(self, contents):
        self.md.reset()
        return self.md.convert(contents)

    def render_contents(self):
        return self.contents["fragment"]

    def get_template_context(self):
        ctx = TemplatedProgram.get_template_context(self)
        ctx["md"] = self.contents
        return ctx
