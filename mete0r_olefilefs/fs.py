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

from fs.base import FS
from fs.errors import CreateFailedError
from fs.errors import OperationFailedError
from olefile import OleFileIO
from olefile import STGTY_ROOT
from olefile import STGTY_STORAGE
from olefile import STGTY_STREAM


class OleFileFS(FS):

    _meta = dict(read_only=True,
                 thread_safe=False,
                 network=False,
                 unicode_paths=True,
                 case_insensitive_paths=True)

    def __init__(self, path):
        try:
            self._olefile = OleFileIO(path, path_encoding=None)
        except IOError as e:
            raise CreateFailedError(str(e), details=e)

    #
    # Essential methods
    #

    def open(self, path, mode='r', buffering=-1, encoding=None, errors=None,
             newline=None, line_buffering=False, **kwargs):
        for unsupported in 'w', 'a', '+':
            if unsupported in mode:
                raise OperationFailedError('open', path=path)
        segments = path_to_segments_normalized(path)
        return self._olefile.openstream(segments)

    def isdir(self, path):
        segments = path_to_segments_normalized(path)
        sty = self._olefile.get_type(segments)
        return sty in (STGTY_STORAGE, STGTY_ROOT)

    def isfile(self, path):
        segments = path_to_segments_normalized(path)
        sty = self._olefile.get_type(segments)
        return sty is STGTY_STREAM

    def listdir(self, path='./', wildcard=None, full=False, absolute=False,
                dirs_only=False, files_only=False):
        items = self.ilistdir(path=path, wildcard=wildcard, full=full,
                              absolute=absolute, dirs_only=dirs_only,
                              files_only=files_only)
        return list(items)

    def getinfo(self, path):
        segments = path_to_segments_normalized(path)
        size = self._olefile.get_size(segments)
        ctime = self._olefile.getctime(segments)
        mtime = self._olefile.getmtime(segments)
        return {
            'size': size,
            'created_time': ctime,
            'modified_time': mtime,
        }

    #
    # Non-essential methods
    #

    def close(self):
        self._olefile.close()
        FS.close(self)

    def ilistdir(self, path='./', wildcard=None, full=False, absolute=False,
                 dirs_only=False, files_only=False):
        if dirs_only:
            olefile_listdir_args = dict(streams=False, storages=True)
        elif files_only:
            olefile_listdir_args = dict(streams=True, storages=False)
        else:
            olefile_listdir_args = dict()
        given_node = path_to_segments_normalized(path)
        leafs = self._olefile.listdir(**olefile_listdir_args)
        leafs = map(tuple, leafs)
        nodes = find_children(given_node, leafs)
        for segments in nodes:
            stgty = self._olefile.get_type(segments)
            if dirs_only and stgty not in (STGTY_STORAGE, STGTY_ROOT):
                continue
            elif files_only and stgty is not STGTY_STREAM:
                continue
            if absolute:
                yield absolute_path_from_segments(segments)
            elif full:
                yield full_path_from_segments(segments)
            else:
                yield segments[-1]


def find_children(prefix, nodes):
    seen = set()
    for node in nodes:
        if segments_is_descendant_of(node, prefix):
            child = node[:len(prefix) + 1]
            if child not in seen:
                yield child
                seen.add(child)


def segments_is_descendant_of(node, ancestor):
    if len(node) <= len(ancestor):
        return False
    return node[:len(ancestor)] == ancestor


def absolute_path_from_segments(segments):
    return '/' + full_path_from_segments(segments)


def full_path_from_segments(segments):
    return '/'.join(segments)


def path_to_segments_normalized(path):
    path = os.path.normpath(path)
    segments = path.split('/')
    if len(segments) > 0 and segments[0] == '.':
        segments = segments[1:]
    segments = filter(lambda x: len(x) > 0, segments)
    segments = tuple(segments)
    return segments
