#!/usr/bin/env python3
"""Convert a CFF-flavored OTF into a TrueType-flavored TTF, keeping every
OpenType layout table (GSUB, GPOS, GDEF, MATH, ...) untouched.

Adapted from Snippets/otf2ttf.py in fontTools (MIT License)."""

import argparse

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

# Approximation error, in em units, when turning cubic curves into quadratic ones
MAX_ERR = 1.0
POST_FORMAT = 2.0
REVERSE_DIRECTION = True


def glyphs_to_quadratic(glyph_set, max_err=MAX_ERR, reverse_direction=REVERSE_DIRECTION):
    quad_glyphs = {}
    for name in glyph_set.keys():
        glyph = glyph_set[name]
        tt_pen = TTGlyphPen(glyph_set)
        cu2qu_pen = Cu2QuPen(tt_pen, max_err, reverse_direction=reverse_direction)
        glyph.draw(cu2qu_pen)
        quad_glyphs[name] = tt_pen.glyph()
    return quad_glyphs


def otf_to_ttf(font, post_format=POST_FORMAT, **kwargs):
    assert font.sfntVersion == "OTTO", "input must be a CFF-flavored OpenType font"
    assert "CFF " in font, "input has no CFF table"

    glyph_order = font.getGlyphOrder()

    font["loca"] = newTable("loca")
    font["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder = glyph_order
    glyf.glyphs = glyphs_to_quadratic(font.getGlyphSet(), **kwargs)
    del font["CFF "]
    if "VORG" in font:
        del font["VORG"]
    glyf.compile(font)
    for name in glyph_order:
        glyf[name].recalcBounds(glyf)

    font["maxp"] = maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    maxp.maxZones = 1
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = max(
        len(g.components if hasattr(g, "components") else []) for g in glyf.glyphs.values()
    )
    maxp.compile(font)

    post = font["post"]
    post.formatType = post_format
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyph_order

    font.sfntVersion = "\000\001\000\000"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input OTF")
    parser.add_argument("output", help="output TTF")
    parser.add_argument("--max-err", type=float, default=MAX_ERR)
    args = parser.parse_args(argv)

    font = TTFont(args.input)
    otf_to_ttf(font, max_err=args.max_err)
    font.save(args.output)


if __name__ == "__main__":
    main()
