from setuptools import setup

setup(
    name='blogdown',
    version='1.0',
    author='Brant Young <brant.young@gmail.com>',
    packages=['blogdown', 'blogdown.modules'],
    description='',
    long_description='',
    license='BSD License',
    entry_points = {
        'console_scripts': ['run-blogdown = blogdown.cli:main'],
    },
    install_requires=['PyYAML', 'Babel', 'blinker', 'Markdown', 'Jinja2>=2.4', 'Werkzeug', 'docutils']
)
