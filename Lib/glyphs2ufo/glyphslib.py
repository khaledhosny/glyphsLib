#!/usr/bin/python
#
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__all__ = [
    "build_masters", "build_instances", "load_to_ufos", "load", "loads",
]

import json
from os import path
import sys

from parser import Parser
from casting import cast_data, cast_custom_data
from torf import to_robofab


def load(fp, dict_type=dict):
	"""Read a .glyphs file. 'fp' should be (readable) file object.
	Return the unpacked root object (which usually is a dictionary).
	"""
	return loads(fp.read(), dict_type=dict_type)


def loads(value, dict_type=dict):
	"""Read a .glyphs file from a bytes object.
	Return the unpacked root object (which usually is a dictionary).
	"""
	p = Parser(dict_type=dict_type)
	print '>>> Parsing .glyphs file'
	data = p.parse(value)
	print '>>> Casting parsed values'
	cast_data(data)
	cast_custom_data(data)
	return data


def load_to_ufos(filename, italic=False, include_instances=False, debug=False):
    """Load an unpacked .glyphs object to a RoboFab RFont."""

    with open(filename, 'rb') as ifile:
        data = load(ifile)
    print '>>> Loading to RFonts'
    return to_robofab(data, italic=italic, include_instances=include_instances,
                      debug=debug)


def write(ufo, out_dir):
    """Write a UFO."""

    if ufo.path:
        print '>>> Writing %s' % ufo.path
        ufo.save()
    else:
        ofile = path.join(out_dir, ufo.info.postscriptFullName + '.ufo')
        print '>>> Writing %s' % ofile
        ufo.save(ofile)


def build_masters(filename, master_dir, italic=False):
    """Write and return UFOs from the masters defined in a .glyphs file."""

    ufos = load_to_ufos(filename, italic)

    for ufo in ufos:
        write(ufo, master_dir)
    return ufos


def build_instances(filename, master_dir, instance_dir, italic=False):
    """Write and return UFOs from the instances defined in a .glyphs file."""

    from interpolation import interpolate

    designspace_path = filename.replace('.glyphs', '.designspace')
    master_ufos, instance_data = load_to_ufos(
        filename, italic, include_instances=True)
    return interpolate(
        master_ufos, master_dir, instance_dir, designspace_path, instance_data)


def main(filename, master_dir='master_ufo', instance_dir='instance_ufo'):
    build_masters(
        filename, master_dir, italic=('Italic' in filename))
    #build_instances(
    #    filename, master_dir, instance_dir, italic=('Italic' in filename))


if __name__ == '__main__':
    main(*sys.argv[1:])