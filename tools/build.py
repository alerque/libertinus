# encoding: utf-8
import argparse
import datetime
import os
import sys

import fontforge

from fontTools import subset
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

for glyph in font.glyphs():
    glyph.unlinkRef()
    if glyph.unlinkRmOvrlpSave:
        glyph.removeOverlap()
    glyph.correctDirection()
    glyph.autoHint()

font.generate(args.output, flags=("opentype"))

ttfont = TTFont(args.output)

# https://github.com/fontforge/fontforge/pull/3235
# fontDirectionHint is deprecated and must be set to 2
ttfont["head"].fontDirectionHint = 2
# unset bits 6..10
ttfont["head"].flags &= ~0x7e0

options = subset.Options()
options.set(layout_features='*', name_IDs='*', notdef_outline=True,
            glyph_names=True, recalc_average_width=True, drop_tables=["FFTM"])

unicodes = ttfont["cmap"].getBestCmap().keys()

subsetter = subset.Subsetter(options=options)
subsetter.populate(unicodes=unicodes)
subsetter.subset(ttfont)

ttfont.save(args.output)
