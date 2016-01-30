import fontforge
import sys

font = fontforge.open(sys.argv[1])
glyphs = {}

for glyph in font.glyphs():
    if glyph.name not in glyphs:
        glyphs[glyph.name] = 0
    glyphs[glyph.name] += 1

duplicates = [g for g in glyphs if glyphs[g] > 1]

if duplicates:
    print "Font has duplicate glyphs: %s" % " ".join(duplicates)
    sys.exit(1)
