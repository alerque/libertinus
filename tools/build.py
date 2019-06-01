# encoding: utf-8
import argparse
import datetime
import os

import fontforge

from fontTools.misc.py23 import StringIO
from pcpp.preprocessor import Preprocessor

from tempfile import NamedTemporaryFile


class Font:
    def __init__(self, filename, features, version):
        self._font = fontforge.open(filename)
        self._version = version

        self._features = StringIO()
        if features:
            preprocessor = Preprocessor()
            for d in ("italic", "sans", "display", "math"):
                if d in filename.lower():
                    preprocessor.define(d.upper())
            with open(features) as f:
                preprocessor.parse(f)
            preprocessor.write(self._features)

    def _merge_features(self):
        font = self._font
        features = self._features

        with NamedTemporaryFile(suffix=".fea", mode="rt") as temp:
            font.generateFeatureFile(temp.name)
            lines = temp.readlines()
            for line in lines:
                if not line.startswith("languagesystem"):
                    features.write(line)

        for lookup in font.gpos_lookups + font.gsub_lookups:
            font.removeLookup(lookup)

        with NamedTemporaryFile(suffix=".fea", mode="w") as temp:
            temp.write(features.getvalue())
            temp.flush()
            font.mergeFeature(temp.name)

    def _cleanup_glyphs(self):
        font = self._font
        for glyph in font.glyphs():
            glyph.unlinkRef()
            if glyph.unlinkRmOvrlpSave:
                glyph.removeOverlap()
            glyph.correctDirection()

    def _update_metadata(self):
        version = self._version
        font = self._font

        year = datetime.date.today().year
        font.copyright = (u"Copyright © 2012-%s " % year +
                          u"The Libertinus Project Authors.")
        font.version = version

        # Override the default which includes the build date
        font.appendSFNTName("English (US)", "UniqueID", "%s;%s;%s" %
                            (version, font.os2_vendor, font.fontname))
        font.appendSFNTName("English (US)", "Vendor URL",
                            "https://github.com/alif-type/libertinus")

    def _draw_over_under_line(self, name, widths):
        font = self._font
        bbox = font[name].boundingBox()
        pos = bbox[1]
        height = bbox[-1] - bbox[1]

        for width in sorted(widths):
            glyph = font.createChar(-1, "%s.%d" % (name, width))
            glyph.width = 0
            glyph.glyphclass = "mark"

            pen = glyph.glyphPen()

            pen.moveTo((-25 - width, pos))
            pen.lineTo((-25 - width, pos + height))
            pen.lineTo((25, pos + height))
            pen.lineTo((25, pos))
            pen.closePath()

    def _make_over_under_line(self):
        font = self._font
        minwidth = 50

        bases = [n for n in ("uni0305", "uni0332") if n in font]
        if not bases:
            return

        # Collect glyphs grouped by their widths rounded by minwidth, we will
        # use them to decide the widths of over/underline glyphs we will draw
        widths = {}
        for glyph in font.glyphs():
            if glyph.glyphclass != 'mark' and glyph.width > 0:
                width = round(glyph.width / minwidth) * minwidth
                width = max(width, minwidth)
                if width not in widths:
                    widths[width] = []
                widths[width].append(glyph.glyphname)

        for name in bases:
            self._draw_over_under_line(name, widths)

        dirname = os.path.dirname(font.path)
        fea = []
        fea.append("feature mark {")
        fea.append("  @OverSet = [%s];" % " ".join(bases))
        fea.append("  lookupflag UseMarkFilteringSet @OverSet;")
        for width in sorted(widths):
            # For each width group we create an over/underline glyph with the
            # same width, and add a contextual substitution lookup to use it
            # when an over/underline follows any glyph in this group
            replacements = ['%s.%d' % (name, width) for name in bases]
            fea.append("  sub [%s] [%s]' by [%s];" % (" ".join(widths[width]),
                                                      " ".join(bases),
                                                      " ".join(replacements)))
        fea.append("} mark;")

        self._features.write("\n".join(fea))

    def generate(self, output):
        self._update_metadata()
        self._cleanup_glyphs()
        self._make_over_under_line()
        self._merge_features()
        self._font.generate(output, flags=("opentype"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("-v", "--version", required=True)
    parser.add_argument("-f", "--feature-file", required=False)

    args = parser.parse_args()
    font = Font(args.input, args.feature_file, args.version)
    font.generate(args.output)


if __name__ == "__main__":
    main()
