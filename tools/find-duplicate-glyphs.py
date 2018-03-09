from __future__ import print_function

import fontforge
import sys

font = fontforge.open(sys.argv[1])
names = [g.glyphname for g in font.glyphs()]
duplicates = set(n for n in names if names.count(n) > 1)

with open(sys.argv[2], "w") as logfile:
    msg = "PASS"
    if duplicates:
        msg = "FAIL: Font has duplicate glyphs: %s" % " ".join(duplicates)
        print(msg)
    print(msg, file=logfile)

sys.exit(len(duplicates))
