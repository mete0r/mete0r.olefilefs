# -*- coding: utf-8 -*-
#
#   mete0r.olefilefs : PyFilesystem interface to olefile
#   Copyright (C) 2015 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import unicode_literals

from unittest import TestCase
import os.path


FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')
TEST_XLS_PATH = os.path.join(FILES_DIR, 'test.xls')
EXAMPLE_STG_PATH = os.path.join(FILES_DIR, 'example.stg')


class OleFileFSTest(TestCase):

    def test_constructor_path(self):
        from ..fs import OleFileFS
        path = TEST_XLS_PATH
        with OleFileFS(path):
            pass

    def test_constructor_filelike(self):
        from ..fs import OleFileFS
        path = TEST_XLS_PATH
        with open(path, 'rb') as f:
            with OleFileFS(f):
                pass

    def test_constructor_nonexists(self):
        from fs.errors import CreateFailedError
        from ..fs import OleFileFS
        try:
            with OleFileFS('nonexists.xls'):
                pass
        except CreateFailedError as e:
            self.assertEquals(e.details.errno, 2)
        else:
            raise AssertionError('CreateFailedError expected')

    def _createOne(self):
        from ..fs import OleFileFS
        return OleFileFS(TEST_XLS_PATH)

    def test_close(self):
        fs = self._createOne()
        fs.close()

    def test_isdir(self):
        with self._createOne() as fs:
            self.assertTrue(fs.isdir('/'))
            self.assertFalse(fs.isdir('Workbook'))

    def test_isfile(self):
        with self._createOne() as fs:
            self.assertFalse(fs.isfile('/'))
            self.assertTrue(fs.isfile('Workbook'))

    def test_listdir(self):
        with self._createOne() as fs:
            items = fs.listdir()
            self.assertEquals(items, [
                '\x01CompObj',
                '\x01Ole',
                '\x05DocumentSummaryInformation',
                '\x05SummaryInformation',
                'Workbook',
            ])

    def test_listdir_dirs_only(self):
        with self._createOne() as fs:
            items = fs.listdir(dirs_only=True)
            self.assertEquals(items, [
            ])

    def test_listdir_files_only(self):
        with self._createOne() as fs:
            items = fs.listdir(files_only=True)
            self.assertEquals(items, [
                '\x01CompObj',
                '\x01Ole',
                '\x05DocumentSummaryInformation',
                '\x05SummaryInformation',
                'Workbook',
            ])

    def test_listdir_files_only_with_deep_streams(self):
        from ..fs import OleFileFS
        with OleFileFS(EXAMPLE_STG_PATH) as fs:
            items = fs.listdir(files_only=True)
            self.assertEquals(items, [
                'a',
                'b',
            ])

    def test_listdir_full(self):
        with self._createOne() as fs:
            items = fs.listdir(full=True)
            self.assertEquals(items, [
                '\x01CompObj',
                '\x01Ole',
                '\x05DocumentSummaryInformation',
                '\x05SummaryInformation',
                'Workbook',
            ])

    def test_listdir_absolute(self):
        with self._createOne() as fs:
            items = fs.listdir(absolute=True)
            self.assertEquals(items, [
                '/\x01CompObj',
                '/\x01Ole',
                '/\x05DocumentSummaryInformation',
                '/\x05SummaryInformation',
                '/Workbook',
            ])

    def test_getinfo(self):
        with self._createOne() as fs:
            info = fs.getinfo('Workbook')
            self.assertEquals(info, {
                'size': 2743,
                'created_time': None,
                'modified_time': None,
            })

    def test_open_w(self):
        from fs.errors import OperationFailedError
        with self._createOne() as fs:
            try:
                with fs.open('new', 'w'):
                    pass
            except OperationFailedError as e:
                self.assertEquals(e.opname, 'open')
                self.assertEquals(e.path, 'new')
            else:
                raise AssertionError('OperationFailedError expected')

    def test_open_a(self):
        from fs.errors import OperationFailedError
        with self._createOne() as fs:
            try:
                with fs.open('new', 'a'):
                    pass
            except OperationFailedError as e:
                self.assertEquals(e.opname, 'open')
                self.assertEquals(e.path, 'new')
            else:
                raise AssertionError('OperationFailedError expected')

    def test_open_rplus(self):
        from fs.errors import OperationFailedError
        with self._createOne() as fs:
            try:
                with fs.open('new', 'r+'):
                    pass
            except OperationFailedError as e:
                self.assertEquals(e.opname, 'open')
                self.assertEquals(e.path, 'new')
            else:
                raise AssertionError('OperationFailedError expected')

    def test_open_for_reading(self):
        with self._createOne() as fs:
            with fs.open('Workbook') as f:
                f.read()

    def test_getmeta(self):
        with self._createOne() as fs:
            self.assertTrue(fs.getmeta('read_only'))
            self.assertFalse(fs.getmeta('thread_safe'))
            self.assertFalse(fs.getmeta('network'))
            self.assertTrue(fs.getmeta('unicode_paths'))
            self.assertTrue(fs.getmeta('case_insensitive_paths'))


class FnsTest(TestCase):

    def test_segments_is_descendant_of(self):
        from ..fs import segments_is_descendant_of
        self.assertTrue(segments_is_descendant_of(('A', 'B'), ()))
        self.assertTrue(segments_is_descendant_of(('A', 'B'), ('A', )))
        self.assertFalse(segments_is_descendant_of(('A', 'B'), ('A', 'C')))
        self.assertFalse(segments_is_descendant_of(('A', 'B'), ('B',)))
        self.assertFalse(segments_is_descendant_of(('A', 'B'), ('A', 'B')))
        self.assertFalse(segments_is_descendant_of(('A',), ('A', 'B')))

    def test_find_children(self):
        from ..fs import find_children
        nodes = [
            ('A',),
            ('B', '01'),
            ('B', '02')
        ]
        items = list(find_children((), nodes))
        self.assertEquals(items, [
            ('A', ),
            ('B', ),
        ])

        items = list(find_children(('B', ), nodes))
        self.assertEquals(items, [
            ('B', '01'),
            ('B', '02')
        ])

        items = list(find_children(('B', ), [
            ('B', ),
            ('B', '01'),
            ('B', '02'),
        ]))
        self.assertEquals(items, [
            ('B', '01'),
            ('B', '02')
        ])

    def test_path_to_segments_normalized(self):
        from ..fs import path_to_segments_normalized
        self.assertEquals(path_to_segments_normalized('/'),
                          ())
        self.assertEquals(path_to_segments_normalized('/A'),
                          ('A', ))
        self.assertEquals(path_to_segments_normalized('/A/'),
                          ('A', ))
        self.assertEquals(path_to_segments_normalized('/A/B'),
                          ('A', 'B'))
        self.assertEquals(path_to_segments_normalized('/A/B/'),
                          ('A', 'B'))
        self.assertEquals(path_to_segments_normalized('.'),
                          ())
        self.assertEquals(path_to_segments_normalized('./'),
                          ())
        self.assertEquals(path_to_segments_normalized('.'),
                          ())
        self.assertEquals(path_to_segments_normalized('./.'),
                          ())
        self.assertEquals(path_to_segments_normalized('..'),
                          ('..', ))
        self.assertEquals(path_to_segments_normalized('A/B/..'),
                          ('A', ))
