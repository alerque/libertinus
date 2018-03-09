from __future__ import print_function

import fontforge
import sys

font = fontforge.open(sys.argv[1])
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

with open(sys.argv[2], "w") as logfile:
    msg = "PASS"
    if missing:
        msg = "Font is missing: %s" % " ".join([n for n in missing])
        print(msg)
    print(msg, file=logfile)

sys.exit(len(missing))
