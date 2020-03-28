from setuptools import setup

setup(
    name='blogdown',
    version='1.3.0',
    author='Blogdown Team',
    author_email='yang@yangyubo.com',
    include_package_data = True,
    packages=['blogdown', 'blogdown.modules'],
    description='a simple static blog generator',
    long_description=open('README.rst').read(),
    license='BSD License',
    url='https://github.com/blogdown/blogdown/',
    entry_points = {
        'console_scripts': ['run-blogdown = blogdown.cli:main'],
    },
    install_requires=[
        'PyYAML',
        'Babel',
        'blinker',
        'Markdown',
        'Jinja2>=2.4',
        'Werkzeug<1.0.0',
        'docutils',
        'pygments',
        'six',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
)
