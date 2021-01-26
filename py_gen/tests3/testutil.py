#!/usr/bin/env python3
# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

import sys
import difflib
import re
import os
import unittest
import test_data
from loxi.generic_util import OFReader

# Human-friendly format for binary strings. 8 bytes per line.
def format_binary(arg):
    if isinstance(arg, str):
        byts = map(ord, arg)
    elif isinstance(arg, bytes):
        byts = arg
    else:
        raise ValueError('unhandled type', arg, type(arg))
    lines = [[]]
    for byt in byts:
        if len(lines[-1]) == 8:
            lines.append([])
        lines[-1].append(byt)
    return '\n'.join([' '.join(['%02x' % y for y in x]) for x in lines])

def diff(a, b):
    return '\n'.join(difflib.ndiff(a.splitlines(), b.splitlines()))

# Test serialization / deserialization / reserialization of a sample object.
# Depends in part on the __eq__ method being correct.
def test_serialization(obj, buf):
    packed = obj.pack()
    if packed != buf:
        a = format_binary(buf)
        b = format_binary(packed)
        raise AssertionError("Serialization of %s failed\nExpected:\n%s\nActual:\n%s\nDiff:\n%s" % \
                             (type(obj).__name__, a, b, diff(a, b)))
    unpacked = type(obj).unpack(OFReader(buf))
    if obj != unpacked:
        a = obj.show()
        b = unpacked.show()
        raise AssertionError("Deserialization of %s failed\nExpected:\n%s\nActual:\n%s\nDiff:\n%s" % \
            (type(obj).__name__, a, b, diff(a, b)))
    packed = unpacked.pack()
    if packed != buf:
        a = format_binary(buf)
        b = format_binary(packed)
        raise AssertionError("Reserialization of %s failed\nExpected:\n%s\nActual:\n%s\nDiff:\n%s" % \
                             (type(obj).__name__, a, b, diff(a, b)))

def test_pretty(obj, expected):
    pretty = obj.show()
    if expected != pretty:
        raise AssertionError("Pretty printing of %s failed\nExpected:\n%s\nActual:\n%s\nDiff:\n%s" % \
            (type(obj).__name__, expected, pretty, diff(expected, pretty)))

# Run test_serialization and possibly test_pretty against the named data file
def test_datafile(name, ofp, pyversion):
    data = test_data.read(name)
    if pyversion == 3:
        key = 'python3'
        if key not in data:
            # default to the 'python' section
            key = 'python'
    else:
        key = 'python'
    if key not in data:
        raise unittest.SkipTest("no %s section in datafile" % key)
    binary = data['binary']
    python = data[key]
    obj = eval(python, { 'ofp': ofp })
    test_serialization(obj, binary)
    keyprettyprint = key + ' pretty-printer'
    if keyprettyprint in data:
        test_pretty(obj, data[keyprettyprint])

# Add test_datafile tests for each datafile matching the given regex
# The argument 'klass' should be a subclass of TestCase which will have the
# test_* methods added to it.
#
# It would be cleaner to do this by constructing a TestSuite instance and
# adding individual TestCase objects, but the TestLoader wouldn't pick it
# up. We could use the load_tests protocol but that isn't available before
# Python 2.7.
def add_datafiles_tests(klass, regex, ofp, pyversion=3):
    for filename in test_data.list_files():
        match = re.match(regex, filename)
        if not match:
            continue
        def make_test(filename):
            def fn(self):
                test_datafile(filename, ofp, pyversion)
            return fn
        setattr(klass, 'test_' + os.path.splitext(filename)[0], make_test(filename))
