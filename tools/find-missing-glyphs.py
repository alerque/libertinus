import fontforge
import sys

font = fontforge.open(sys.argv[1])
missing = set()

for glyph in font.glyphs():
    for lookup in font.gsub_lookups:
        for subtable in font.getLookupSubtables(lookup):
            for possub in glyph.getPosSub(subtable):
                missing.update([n for n in possub[2:] if n not in font])
if missing:
    print "Font is missing: %s" % " ".join([n for n in missing])
    sys.exit(1)
