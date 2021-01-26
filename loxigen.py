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

"""
@brief
Process openflow header files to create language specific LOXI interfaces

First cut at simple python script for processing input files

Internal notes

An input file for each supported OpenFlow version is passed in
on the command line.

Expected input file format:

These will probably be collapsed into a python dict or something

The first line has the ofC version identifier and nothing else
The second line has the openflow wire protocol value and nothing else

The main content is struct elements for each OF recognized class.
These are taken from current versions of openflow.h but are modified
a bit.  See Overview for more information.

Class canonical form:   A list of entries, each of which is a
pair "type, name;".  The exception is when type is the keyword
'list' in which the syntax is "list(type) name;".

From this, internal representations are generated:  For each
version, a dict indexed by class name.  One element (members) is
an array giving the member name and type.  From this, wire offsets
can be calculated.


@fixme Clean up the lang module architecture.  It should provide a
list of files that it wants to generate and maps to the filenames,
subdirectory names and generation functions.  It should also be
defined as a class, probably with the constructor taking the
language target.

@fixme Clean up global data structures such as versions and of_g
structures.  They should probably be a class or classes as well.

"""

from collections import OrderedDict, defaultdict
import copy
import glob
from optparse import OptionParser
import os
import re
import string
import sys

import cmdline
from loxi_globals import OFVersions
import loxi_globals
import loxi_utils.loxi_utils as loxi_utils
import pyparsing
import loxi_front_end.parser as parser
import loxi_front_end.frontend as frontend
import loxi_ir
from generic_utils import *

root_dir = os.path.dirname(os.path.realpath(__file__))

def process_input_file(filename):
    """
    Process an input file

    Does not modify global state.

    @param filename The input filename

    @returns An OFInput object
    """

    # Parse the input file
    try:
        # handle other encodings without throwing UnicodeDecodeError
        with open(filename, encoding='utf-8', errors='replace') as f:
            ast = parser.parse(f.read())
    except pyparsing.ParseBaseException as e:
        print("Parse error in %s: %s" % (os.path.basename(filename), str(e)))
        sys.exit(1)

    # Create the OFInput from the AST
    try:
        ofinput = frontend.create_ofinput(os.path.basename(filename), ast)
    except frontend.InputError as e:
        print("Error in %s: %s" % (os.path.basename(filename), str(e)))
        sys.exit(1)

    return ofinput

def read_input():
    """
    Read in from files given on command line and update global state

    @fixme Should select versions to support from command line
    """

    ofinputs_by_version = defaultdict(lambda: [])
    filenames = sorted(glob.glob("%s/openflow_input/*" % root_dir))

    # Ignore emacs backup files
    filenames = [x for x in filenames if not x.endswith('~')]

    # Read input files
    for filename in filenames:
        log("Processing struct file: " + filename)
        ofinput = process_input_file(filename)

        for wire_version in ofinput.wire_versions:
            version = loxi_globals.OFVersions.from_wire(wire_version)
            if version in loxi_globals.OFVersions.target_versions:
                ofinputs_by_version[wire_version].append(ofinput)
    return ofinputs_by_version

def build_ir(ofinputs_by_version):
    classes = []
    enums = []
    for wire_version, ofinputs in ofinputs_by_version.items():
        version = OFVersions.from_wire(wire_version)
        ofprotocol = loxi_ir.build_protocol(version, ofinputs)
        loxi_globals.ir[version] = ofprotocol

    loxi_globals.unified = loxi_ir.build_unified_ir(loxi_globals.ir)
    # uncomment to dump the internal represenation for a given version
    #print(loxi_globals.ir[OFVersions.VERSION_1_4])

################################################################
#
# Debug
#
################################################################

if __name__ == '__main__':
    (options, args, target_versions) = cmdline.process_commandline()
    # @fixme Use command line params to select log

    logging.basicConfig(level = logging.INFO if not options.verbose else logging.DEBUG)

    # Import the language file
    lang_file = "lang_%s" % options.lang
    lang_module = __import__(lang_file)

    log("\nGenerating files for target language %s\n" % options.lang)

    loxi_globals.OFVersions.target_versions = target_versions
    inputs = read_input()
    build_ir(inputs)
    lang_module.generate(options.install_dir)
