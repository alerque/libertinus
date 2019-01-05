# encoding: utf-8
import argparse
import datetime
import os

import fontforge

from fontTools import subset
from fontTools.ttLib import TTFont

from tempfile import NamedTemporaryFile


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
        bases = ["uni0305", "uni0332"]
        minwidth = 50

        if any([name not in font for name in bases]):
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
        fea.append("include(%s/features/langsys.fea)" % dirname)
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

        with NamedTemporaryFile(suffix=".fea") as temp:
            temp.write("\n".join(fea).encode("utf-8"))
            temp.flush()
            font.mergeFeature(temp.name)

    def generate(self, version, output):
        self._update_metadata(version)
        self._cleanup_glyphs()
        self._make_over_under_line()
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
