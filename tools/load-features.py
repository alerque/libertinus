#!/usr/bin/env python

# load OpenType features 
# (c) 2018 Skef Iterum
#
# usage: load-features.py [-e | -f f.fea] -o out.sfd in.sfd

import argparse
import sys
import os
import re
import fontforge

default_configname = 'feature_config.py'
sfd_dir = '.'
feature_file_dir = '.'

parser = argparse.ArgumentParser(
        description="reload_features.py: Reinit contents of a FontForge OpenType feature from a feature file")
parser.add_argument('-f', '--ffile', metavar='(feature_file)')
parser.add_argument('-o', '--output', metavar='(output_file)', required=True)
parser.add_argument('-e', '--empty', action='store_true', help='Remove GSUB entries without replacing')
parser.add_argument('input_file')

args = parser.parse_args()

if not os.path.exists(args.input_file):
    sys.stderr.write("Error: Input file '" + args.input_file + "' not found")
    sys.exit(2)

if args.ffile and args.empty:
    sys.stderr.write("Error: arguments --empty and --ffile are not compatible")

if args.ffile and not os.path.exists(args.ffile):
    sys.stderr.write("Error: Feature file '" + args.ffile + "' not found")
    sys.exit(2)

def empty_gsub(ff):
    for gsublname in ff.gsub_lookups:
        ff.removeLookup(gsublname)

def merge_features(ff, feaname):
    ff.mergeFeature(feaname);

ff = fontforge.open(args.input_file)
empty_gsub(ff)
if args.ffile:
    merge_features(ff, args.ffile)
ff.save(args.output)
