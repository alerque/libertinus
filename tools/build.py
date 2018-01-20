# encoding: utf-8
import sys
try:
    from sortsmill import ffcompat as fontforge
except ImportError:
    print >> sys.stderr, "Failed to import sortsmill, failing back to fontforge"
    import fontforge
import argparse
from datetime import date
from os import path

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-v", "--version", required=True)
parser.add_argument("-f", "--feature-file", required=False)

args = parser.parse_args()

font = fontforge.open(args.input)

if args.feature_file and path.isfile(args.feature_file):
    font.mergeFeature(args.feature_file)

font.version = args.version
font.copyright = u"Copyright © 2012-%s The Libertinus Project Authors." % date.today().year

font.selection.all()
font.autoHint()
font.generate(args.output, flags=("opentype", "no-mac-names"))
