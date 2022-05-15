# -*- coding: utf-8 -*-
"""
    blogdown.plugin
    ~~~~~~~~~~~~~~~

    Utilities for a simple plugin system.

    :copyright: (c) 2015 by Thomas Gläßle
    :license: BSD, see LICENSE for more details.
"""
import os
from importlib import import_module
from pkg_resources import iter_entry_points
from runpy import run_path


__all__ = [
    'EntryPointLoader',
    'PathLoader',
    'PackageLoader',
    'ChainLoader',
]


class EntryPointLoader:

    """Load plugins from specified entrypoint group."""

    def __init__(self, ep_group):
        self.ep_group = ep_group

    def __call__(self, name):
        for ep in iter_entry_points(self.ep_group, name):
            yield ep.load()


class PathLoader:

    """Load plugins from specified folder."""

    def __init__(self, search_path):
        self.search_path = os.path.abspath(search_path)

    def __call__(self, name):
        module_path = os.path.join(self.search_path, name + '.py')
        if not os.path.isfile(module_path):
            return
        module = run_path(module_path)
        try:
            yield module['setup']
        except KeyError:
            raise AttributeError(
                "Module at {0!r} can't be used as a plugin, "
                "since it has no 'setup' function."
                .format(module_path))


class PackageLoader:

    """Load plugins from specified package."""

    def __init__(self, package_name):
        self.package_name = package_name

    def __call__(self, module_name):
        try:
            module = import_module(self.package_name + '.' + module_name)
        except ImportError:
            return
        try:
            yield module.setup
        except AttributeError:
            raise AttributeError(
                "{0!r} can't be used as a plugin, "
                "since it has no 'setup' function."
                .format(module))


class ChainLoader:

    """Load plugins from all of the sub-loaders."""

    def __init__(self, loaders):
        self.loaders = loaders

    def __call__(self, name):
        for loader in self.loaders:
            for plugin in loader(name):
                yield plugin
