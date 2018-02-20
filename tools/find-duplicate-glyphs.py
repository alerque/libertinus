from __future__ import print_function

import fontforge
import sys

font = fontforge.open(sys.argv[1])
glyphs = {}

for glyph in font.glyphs():
    name = glyph.glyphname
    if name not in glyphs:
        glyphs[name] = 0
    glyphs[name] += 1

duplicates = [g for g in glyphs if glyphs[g] > 1]

if duplicates:
    print("Font has duplicate glyphs: %s" % " ".join(duplicates))
    sys.exit(1)
