import os
import shutil
import subprocess
import unittest
from tempfile import TemporaryDirectory


class TestExample(unittest.TestCase):

    def test_blog(self):

        with TemporaryDirectory() as temp_dir:
            shutil.copytree(
                'example/blog', temp_dir,
                dirs_exist_ok=True,
                ignore=ignore_diritem('example/blog', '_build'))
            shutil.rmtree(
                os.path.join(temp_dir, '_build'),
                ignore_errors=True)

            command = ['blogdown', 'build']
            stdout = subprocess.check_output(command, cwd=temp_dir)
            self.assertCountEqual(stdout.splitlines(), [
                b'A about.rst',
                b'A 2022/02/02/dlc.rst',
                b'A 2022/02/02/dlc.sh',
                b'A 2022/02/28/links.rst',
                b'A 2022/02/05/lists.rst',
                b'A 2022/02/21/codeblocks.rst',
                b'A static/style.css',
            ])
            print(stdout.decode('utf-8'))

            build_dir = os.path.join(temp_dir, '_build')
            built_files = sorted([
                os.path.relpath(os.path.join(root, file), build_dir)
                for root, dirs, files in os.walk(build_dir)
                for file in files
            ])
            self.assertEqual(built_files, [
                '2022/02/02/dlc.sh',
                '2022/02/02/dlc/index.html',
                '2022/02/05/lists/index.html',
                '2022/02/21/codeblocks/index.html',
                '2022/02/28/links/index.html',
                '2022/02/index.html',
                '2022/index.html',
                'about/index.html',
                'archive/index.html',
                'feed.atom',
                'index.html',
                'static/_pygments.css',
                'static/style.css',
                'tags/coding/feed.atom',
                'tags/coding/index.html',
                'tags/howto/feed.atom',
                'tags/howto/index.html',
                'tags/index.html',
                'tags/lorem/feed.atom',
                'tags/lorem/index.html',
                'tags/python/feed.atom',
                'tags/python/index.html',
                'tags/rst/feed.atom',
                'tags/rst/index.html',
                'tags/text/feed.atom',
                'tags/text/index.html',
            ])


def ignore_diritem(dir_, name):
    return lambda src, names: [name] if src == dir_ else []


if __name__ == '__main__':
    unittest.main()
