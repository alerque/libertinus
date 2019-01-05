# encoding: utf-8
import argparse
import datetime
import os

import fontforge

from fontTools import subset
from fontTools.ttLib import TTFont


class Font:
    def __init__(self, filename, features):
        self._font = fontforge.open(filename)
        if features and os.path.isfile(features):
            self._font.mergeFeature(features)

    def _cleanup_glyphs(self):
        font = self._font
        for glyph in font.glyphs():
            glyph.unlinkRef()
            if glyph.unlinkRmOvrlpSave:
                glyph.removeOverlap()
            glyph.correctDirection()
            glyph.autoHint()

    def _update_metadata(self, version):
        font = self._font

        year = datetime.date.today().year
        font.copyright = (u"Copyright © 2012-%s " % year +
                          u"The Libertinus Project Authors.")
        font.version = version

        # Override the default which includes the build date
        font.appendSFNTName("English (US)", "UniqueID", "%s;%s;%s" %
                            (version, font.os2_vendor, font.fontname))

    def generate(self, version, output):
        self._update_metadata(version)
        self._cleanup_glyphs()
        self._font.generate(output, flags=("opentype"))

        font = TTFont(output)

        # https://github.com/fontforge/fontforge/pull/3235
        # fontDirectionHint is deprecated and must be set to 2
        font["head"].fontDirectionHint = 2
        # unset bits 6..10
        font["head"].flags &= ~0x7e0

        options = subset.Options()
        options.set(layout_features='*', name_IDs='*', notdef_outline=True,
                    glyph_names=True, recalc_average_width=True,
                    drop_tables=["FFTM"])

        unicodes = font["cmap"].getBestCmap().keys()

        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=unicodes)
        subsetter.subset(font)

        font.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("-v", "--version", required=True)
    parser.add_argument("-f", "--feature-file", required=False)

    args = parser.parse_args()
    font = Font(args.input, args.feature_file)
    font.generate(args.version, args.output)


if __name__ == "__main__":
    main()
