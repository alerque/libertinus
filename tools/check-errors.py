from __future__ import print_function

import fontforge
import sys

font = fontforge.open(sys.argv[1])
names = [g.glyphname for g in font.glyphs()]
duplicates = set(n for n in names if names.count(n) > 1)

missing = set()
for lookup in font.gsub_lookups + font.gpos_lookups:
    kind = font.getLookupInfo(lookup)[0]
    for subtable in font.getLookupSubtables(lookup):
        if "context" in kind:
            # no API to get the context
            pass
        elif "gsub" in kind:
            for glyph in font.glyphs():
                for possub in glyph.getPosSub(subtable):
                    missing.update([n for n in possub[2:] if n not in font])

failed = len(missing) + len(duplicates)
with open(sys.argv[2], "w") as logfile:
    if failed == 0:
        print("PASS", file=logfile)

    if duplicates:
        msg = "FAIL: Font has duplicate glyphs: %s" % " ".join(duplicates)
        print(msg)
        print(msg, file=logfile)
    if missing:
        msg = "Font is missing: %s" % " ".join([n for n in missing])
        print(msg)
        print(msg, file=logfile)

sys.exit(failed)
