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


class OpenerTest(TestCase):

    def test_get_fs(self):
        from fs.opener import OpenerRegistry
        from fs.opener import opener as opener_base
        from ..fs import OleFileFS
        from ..opener import Opener

        openers = sorted(opener_base.openers.items())
        openers = list(value for index, value in openers)
        registry = OpenerRegistry(openers + [Opener])

        fs, path = Opener.get_fs(registry=registry,
                                 fs_name='olefile',
                                 fs_name_params=None,
                                 fs_path=TEST_XLS_PATH + '/Workbook',
                                 writable=False,
                                 create_dir=False)
        self.assertEquals(type(fs), OleFileFS)
        self.assertEquals(path, 'Workbook')

    def test_functional_test(self):
        from fs.opener import OpenerRegistry
        from fs.opener import opener as opener_base
        from ..opener import Opener

        openers = sorted(opener_base.openers.items())
        openers = list(opener for index, opener in openers)
        registry = OpenerRegistry(openers + [Opener])
        with registry.open('olefile://' + TEST_XLS_PATH + '/Workbook'):
            pass
