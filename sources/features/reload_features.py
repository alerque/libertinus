#!/usr/bin/env python

# reload OTF features 
# (c) 2018 Skef Iterum
#
# usage: ./reload_features.py [-e] [-c] typename
#  will rewrite files in place

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
parser.add_argument('-c', '--config', metavar='(config_file)')
parser.add_argument('-e', '--empty', action='store_true', help='Remove subtable entries without replacing')
parser.add_argument('type')

args = parser.parse_args()

if args.config:
    cfile = args.config
else:
    cfile = default_configname

if not os.path.exists(cfile):
    sys.stderr.write("Error: Configuration file '" + cfile + "' not found.")
    sys.exit(2)

# read in feature configuration
exec(open(cfile, 'r').read())

if not file_spec.get(args.type):
    sys.stderr.write("Error: No configuration found for feature set '" + args.type + "'.")
    sys.exit(2)

spec = file_spec[args.type]

# Uses globals sfd_dir and feature_file_dir set in config file
def reload_table(feafile, variants, tabletups, lookuptups = [], empty = False):
    for v in variants:
        print("Processing file " + v)
        ff = fontforge.open(os.path.join(sfd_dir, v))
        # Remove existing entries from tables
        print("  Removing existing subtable entries")
        for g in ff.glyphs():
            for etab, ntab in tabletups:
                ps = g.getPosSub(etab)
                if len(ps) > 0 and len(ps[0]) > 0 and ps[0][0] == etab:
                    g.removePosSub(etab)

        if not empty:
            # merge in the replacement feature file
            print("  Merging feature file " + feafile)
            ff.mergeFeature(os.path.join(feature_file_dir, feafile))
            for etab, ntab in tabletups:
                el = ff.getLookupOfSubtable(etab)
                nl = ff.getLookupInfo(ntab)
                # Merge the added lookup into the existing one
                print("  Merging " + ntab + " into " + etab)
                ff.mergeLookups(el, ntab)
                # Merge the entries of the added subtable into the (now empty) existing one
                ff.mergeLookupSubtables(etab, ntab + ' subtable')
        for elook, nlook in lookuptups:
            print("  Removing contextual lookup subtables from " + elook)
            for elooksub in ff.getLookupSubtables(elook):
                ff.removeLookupSubtable(elooksub)
            if not empty:
                print("  Adding contextual lookup subtables from " + nlook + " into " + elook)
                ff.mergeLookups(elook, nlook)
        print("Saving file " + v)
        ff.save()

for fn in spec['files']:
    m = re.search('_(.*)\.', fn)
    if not m:
        sys.stderr.write("Error: Unrecognized file group for name '" + fn + "'.")
        sys.exit(2)
    g = m.group(1)
    if not variants.get(g):
        sys.stderr.write("Error: Unknown file group '" + g + "'.")
        sys.exit(2)
    v = variants[g]
    t = spec['tables']
    if isinstance(t, dict):
        t = t[g]
    l = spec.get('lookups', [])
    if isinstance(l, dict):
        l = l[g]
    reload_table(fn, v, t, l, args.empty)
