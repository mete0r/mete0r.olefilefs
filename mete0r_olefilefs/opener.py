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
import os.path

from fs.errors import ResourceNotFoundError
from fs.errors import ResourceInvalidError
from fs.opener import Opener as OpenerBase

from .fs import OleFileFS


class Opener(OpenerBase):

    names = ['olefile']
    desc = 'syntax: olefile://<path-to-ole-file>'

    @classmethod
    def get_fs(cls, registry, fs_name, fs_name_params, fs_path, writable,
               create_dir):
        mount = fs_path
        segments = []
        while True:
            try:
                f = registry.open(mount, 'rb')
            except (ResourceNotFoundError,
                    ResourceInvalidError):
                mount, name = os.path.split(mount)
                segments[0:0] = [name]
                continue
            else:
                return OleFileFS(f), '/'.join(segments)
