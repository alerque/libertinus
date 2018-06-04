# encoding: utf-8
import argparse
import datetime
import os
import sys

import fontforge

from fontTools.ttLib import TTFont

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-v", "--version", required=True)
parser.add_argument("-f", "--feature-file", required=False)

args = parser.parse_args()

font = fontforge.open(args.input)

if args.feature_file and os.path.isfile(args.feature_file):
    font.mergeFeature(args.feature_file)

font.version = args.version
font.copyright = u"Copyright © 2012-%s The Libertinus Project Authors." % datetime.date.today().year

# Override the default which includes the build date
font.appendSFNTName("English (US)", "UniqueID", "%s;%s;%s" % (args.version, font.os2_vendor, font.fontname))

font.selection.all()
font.autoHint()
font.generate(args.output, flags=("opentype"))

ttfont = TTFont(args.output)

# Filter-out useless Macintosh names
ttfont["name"].names = [n for n in ttfont["name"].names if n.platformID != 1]

# https://github.com/fontforge/fontforge/pull/3235
# fontDirectionHint is deprecated and must be set to 2
ttfont["head"].fontDirectionHint = 2
# unset bits 6..10
ttfont["head"].flags &= ~0x7e0

# Drop useless table with timestamp
if "FFTM" in ttfont:
    del ttfont["FFTM"]

ttfont.save(args.output)
