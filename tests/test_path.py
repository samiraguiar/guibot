#!/usr/bin/python3
# Copyright 2013-2018 Intranet AG and contributors
#
# guibot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# guibot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with guibot.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import unittest
import shutil
from tempfile import mkdtemp, mkstemp

import common_test
from guibot.path import Path, ScopedPath
from guibot.errors import *


class PathTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Change to 'tests' directory
        self.saved_working_dir = os.getcwd()
        os.chdir(common_test.unittest_dir)

    @classmethod
    def tearDownClass(self):
        os.chdir(self.saved_working_dir)

    def setUp(self):
        self.path = Path()

        # Clear paths from any previous unit test since
        # the paths are shared between all Path instances
        self.path.clear()

    def test_basic(self):
        self.path.add_path('paths')

    def test_remove_path(self):
        self.path.add_path('images')
        self.assertEqual(True, self.path.remove_path('images'))
        self.assertEqual(False, self.path.remove_path('images'))

    def test_remove_unknown_path(self):
        self.path.remove_path('foobar_does_not_exist')

    def test_search(self):
        self.path.add_path('images')
        self.assertEqual('images/shape_black_box.png', self.path.search('shape_black_box.png'))

        # Create another Path instance - it should contain the same search paths
        new_finder = Path()
        self.assertEqual('images/shape_black_box.png', new_finder.search('shape_black_box'))

    def test_search_fail(self):
        self.path.add_path('images')

        # Test failed search
        try:
            target = self.path.search('foobar_does_not_exist')
            self.fail('Exception not thrown')
        except FileNotFoundError as e:
            pass

    def test_search_type(self):
        self.path.add_path('images')

        # Test without extension
        self.assertEqual('images/shape_black_box.png', self.path.search('shape_black_box'))
        self.assertEqual('images/mouse down.txt', self.path.search('mouse down'))
        self.assertEqual('images/circle.steps', self.path.search('circle'))

        # Test correct precedence of the checks
        self.assertEqual('images/shape_blue_circle.pth', self.path.search('shape_blue_circle.pth'))
        self.assertEqual('images/shape_blue_circle.xml', self.path.search('shape_blue_circle.xml'))
        self.assertEqual('images/shape_blue_circle.png', self.path.search('shape_blue_circle'))

    def test_search_keyword(self):
        self.path.add_path('images')
        self.assertEqual('images/shape_black_box.png', self.path.search('shape_black_box.png', 'images'))

        # Fail if the path restriction results in an empty set
        try:
            target = self.path.search('shape_black_box.png', 'other-images')
            self.fail('Exception not thrown')
        except FileNotFoundError as e:
            pass

    def test_search_silent(self):
        self.path.add_path('images')
        self.assertEqual('images/shape_black_box.png', self.path.search('shape_black_box.png', silent=True))

        # Fail if the path restriction results in an empty set
        target = self.path.search('shape_missing_box.png', silent=True)
        self.assertIsNone(target)


class ScopedPathTest(unittest.TestCase):
    def test_scoped_paths(self):
        """
        Test if scoped paths work correctly.
        """
        # temporary directory 1
        tmp_dir1 = mkdtemp()
        fd_tmp_file1, tmp_file1 = mkstemp(prefix=f"{tmp_dir1}/", suffix=".txt")
        os.close(fd_tmp_file1)

        # temporary directory 2
        tmp_dir2 = mkdtemp()
        fd_tmp_file2, tmp_file2 = mkstemp(prefix=f"{tmp_dir2}/", suffix=".txt")
        os.close(fd_tmp_file2)

        filename1 = os.path.basename(tmp_file1)
        filename2 = os.path.basename(tmp_file2)
        try:
            path = Path()
            path.add_path(tmp_dir1)
            path.add_path(tmp_dir2)
            # sanity check - assert that normal path resolution works
            self.assertEqual(path.search(filename1), tmp_file1)
            self.assertEqual(path.search(filename2), tmp_file2)

            # now check that only one of these are found in our scope
            with ScopedPath(tmp_dir2) as p:
                self.assertEqual(p.search(filename2), tmp_file2)
                self.assertRaises(FileNotFoundError, p.search, filename1)

            # finally check that we've correctly restored everything on exit
            self.assertEqual(path.search(filename1), tmp_file1)
            self.assertEqual(path.search(filename2), tmp_file2)
        finally:
            # clean up
            Path().remove_path(os.path.dirname(tmp_dir1))
            shutil.rmtree(tmp_dir1)
            shutil.rmtree(tmp_dir2)


if __name__ == '__main__':
    unittest.main()
