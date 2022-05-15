# -*- coding: utf-8 -*-
"""
    blogdown.modules.blog
    ~~~~~~~~~~~~~~~~~~~~~

    The blog component.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement
from __future__ import unicode_literals

from datetime import datetime, date

from pytz import timezone

import six
urljoin = six.moves.urllib.parse.urljoin

from jinja2 import pass_context

from werkzeug.routing import Rule, Map, NotFound
from feedgen.feed import FeedGenerator

from blogdown.signals import after_file_published, \
     before_build_finished
from blogdown.utils import Pagination


class MonthArchive(object):

    def __init__(self, builder, year, month, entries):
        self.builder = builder
        self.year = year
        self.month = month
        self.entries = entries
        entries.sort(key=lambda x: x.pub_date, reverse=True)

    @property
    def month_name(self):
        return self.builder.format_date(date(int(self.year),
                                        int(self.month), 1),
                                        format='MMMM')

    @property
    def count(self):
        return len(self.entries)


class YearArchive(object):

    def __init__(self, builder, year, months):
        self.year = year
        self.months = [MonthArchive(builder, year, month, entries)
                       for month, entries in months.items()]
        self.months.sort(key=lambda x: -int(x.month))
        self.count = sum(len(x.entries) for x in self.months)


def test_pattern(path, pattern):
    pattern = '/' + pattern.strip('/') + '/<path:extra>'
    adapter = Map([Rule(pattern)]).bind('dummy.invalid')
    try:
        endpoint, values = adapter.match(path.strip('/'))
    except NotFound:
        return
    return values['year'], values['month'], values['day']


def process_blog_entry(context):
    if context.pub_date is None:
        pattern = context.config.get('modules.blog.pub_date_match',
                                     '/<int:year>/<int:month>/<int:day>/')
        tz = timezone(context.config.get('timezone'))
        if pattern is not None:
            rv = test_pattern(context.slug, pattern)
            if rv is not None:
                context.pub_date = datetime(*rv, tzinfo=tz)

    if context.pub_date is None or context.title is None:
        return

    context.builder.get_storage('blog') \
        .setdefault(context.pub_date.year, {}) \
        .setdefault(('0%d' % context.pub_date.month)[-2:], []) \
        .append(context)


def get_all_entries(builder):
    """Returns all blog entries in reverse order"""
    result = []
    storage = builder.get_storage('blog')
    for year, months in storage.items():
        for month, contexts in months.items():
            result.extend(contexts)
    result.sort(key=lambda x: (x.pub_date, x.config.get('day-order', 0)),
                reverse=True)
    return result


def get_archive_summary(builder):
    """Returns a summary of the stuff in the archives."""
    storage = builder.get_storage('blog')
    years = sorted(storage.items(), key=lambda x: -x[0])
    return [YearArchive(builder, year, months) for year, months in years]


@pass_context
def get_recent_blog_entries(context, limit=10):
    return get_all_entries(context['builder'])[:limit]


def write_index_page(builder):
    use_pagination = builder.config.root_get('modules.blog.use_pagination', True)
    per_page = builder.config.root_get('modules.blog.per_page', 10)
    entries = get_all_entries(builder)
    pagination = Pagination(builder, entries, 1, per_page, 'blog_index')
    while 1:
        with builder.open_link_file('blog_index', page=pagination.page) as f:
            rv = builder.render_template('blog/index.html', {
                'pagination':       pagination,
                'show_pagination':  use_pagination
            })
            f.write(rv + '\n')
            if not use_pagination or not pagination.has_next:
                break
            pagination = pagination.get_next()


def write_archive_pages(builder):
    archive = get_archive_summary(builder)
    with builder.open_link_file('blog_archive') as f:
        rv = builder.render_template('blog/archive.html', {
            'archive':      archive
        })
        f.write(rv + '\n')

    for entry in archive:
        with builder.open_link_file('blog_archive', year=entry.year) as f:
            rv = builder.render_template('blog/year_archive.html', {
                'entry':    entry
            })
            f.write(rv + '\n')
        for subentry in entry.months:
            with builder.open_link_file('blog_archive', year=entry.year,
                                        month=subentry.month) as f:
                rv = builder.render_template('blog/month_archive.html', {
                    'entry':    subentry
                })
                f.write(rv + '\n')


def write_feed(builder):
    blog_author = builder.config.root_get('author')
    url = builder.config.root_get('canonical_url') or 'http://localhost/'
    name = builder.config.get('feed.name') or u'Recent Blog Posts'
    subtitle = builder.config.get('feed.subtitle') or u'Recent blog posts'
    feed_url = urljoin(url, builder.link_to('blog_feed'))
    feed = FeedGenerator()
    feed.id(feed_url)
    feed.link(href=url)
    feed.link(href=feed_url, rel='self')
    feed.title(name)
    feed.subtitle(subtitle)

    for entry in get_all_entries(builder)[:10]:
        fe = feed.add_entry()
        fe.id(urljoin(url, entry.slug))
        fe.link(href=fe.id(), rel='self')
        fe.title(entry.title)
        fe.content(six.text_type(entry.render_contents()), type='html')
        fe.author(name=blog_author)
        fe.updated(entry.pub_date)
    with builder.open_link_file('blog_feed') as f:
        f.write(feed.atom_str().decode('utf-8') + '\n')


def write_blog_files(builder):
    write_index_page(builder)
    write_archive_pages(builder)
    write_feed(builder)


def setup(builder):
    after_file_published.connect(process_blog_entry)
    before_build_finished.connect(write_blog_files)
    builder.register_url('blog_index', config_key='modules.blog.index_url',
                         config_default='/', defaults={'page': 1})
    builder.register_url('blog_index', config_key='modules.blog.paged_index_url',
                         config_default='/page/<page>/')
    builder.register_url('blog_archive', config_key='modules.blog.archive_url',
                         config_default='/archive/')
    builder.register_url('blog_archive',
                         config_key='modules.blog.year_archive_url',
                         config_default='/<year>/')
    builder.register_url('blog_archive',
                         config_key='modules.blog.month_archive_url',
                         config_default='/<year>/<month>/')
    builder.register_url('blog_feed', config_key='modules.blog.feed_url',
                         config_default='/feed.atom')
    builder.jinja_env.globals.update(
        get_recent_blog_entries=get_recent_blog_entries
    )
