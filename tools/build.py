import fontforge
import sys

font = fontforge.open(sys.argv[1])

if len(sys.argv) > 4:
  font.mergeFeature(sys.argv[4])

font.mergeFonts("it.sfd")
font.mergeFonts("bf.sfd")
font.mergeFonts("bi.sfd")
font.mergeFonts("sfup.sfd")
font.mergeFonts("sfit.sfd")
font.mergeFonts("sfbf.sfd")

font.version = sys.argv[3]
font.generate(sys.argv[2], flags=("round", "opentype"))
