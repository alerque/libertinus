from __future__ import print_function

import fontforge
import sys

font = fontforge.open(sys.argv[1])
names = [g.glyphname for g in font.glyphs()]
duplicates = set(n for n in names if names.count(n) > 1)

missing = set()
empty_subtables = set()

def isMissing(font, name):
    if name not in font:
        return True

    return not font[name].isWorthOutputting()

for lookup in font.gsub_lookups + font.gpos_lookups:
    kind = font.getLookupInfo(lookup)[0]
    for subtable in font.getLookupSubtables(lookup):
        if "context" in kind:
            # no API to get the context
            pass
        elif "gsub" in kind:
            for glyph in font.glyphs():
                for sub in glyph.getPosSub(subtable):
                    missing.update([n for n in sub[2:] if isMissing(font, n)])
            if not any(g.getPosSub(subtable) for g in font.glyphs()):
                empty_subtables.add(subtable)

failed = len(missing) + len(duplicates) + len(empty_subtables)
with open(sys.argv[2], "w") as logfile:
    if failed == 0:
        print("PASS", file=logfile)

    if duplicates:
        msg = "FAIL: Font has duplicate glyphs: %s" % " ".join(duplicates)
        print(msg)
        print(msg, file=logfile)
    if missing:
        msg = "FAIL: Font is missing: %s" % " ".join(missing)
        print(msg)
        print(msg, file=logfile)
    if empty_subtables:
        msg = "FAIL: Font contains empty lookups:\n%s" % "\n".join(sorted(empty_subtables))
        print(msg)
        print(msg, file=logfile)

sys.exit(failed)
