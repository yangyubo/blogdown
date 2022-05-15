BlogDown
========

`BlogDown <https://github.com/brantyoung/blogdown/>`_ is a simple static blog generator,
forked from `Armin Ronacher <http://lucumr.pocoo.org/>`_'s `rstblog <https://github.com/mitsuhiko/rstblog/>`_.

Project Status
--------------

The project is currently not well maintained and hasn't been upgraded to newer
versions of its dependencies.

Users are recommended to consider alternative static site generators.

Features
--------

BlogDown support both reStructuredText and Markdown markup.

BlogDown can be extended by plugins. The search path is configured by the
config variable ``plugin_folders`` and defaults to ``_plugins``. Plugins can
also be installed using the ``blogdown.plugin`` entrypoint. For examples,
see the files in ``blogdown/modules``.
