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

with open(sys.argv[2], "w") as logfile:
    msg = "PASS"
    if duplicates:
        msg = "FAIL: Font has duplicate glyphs: %s" % " ".join(duplicates)
        print(msg)
    print(msg, file=logfile)

sys.exit(len(duplicates))
