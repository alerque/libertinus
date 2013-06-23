import fontforge
import sys

font = fontforge.open(sys.argv[1])

if len(sys.argv) > 4:
  font.mergeFeature(sys.argv[4])

font.mergeFonts("sources/it.sfd")
font.mergeFonts("sources/bf.sfd")
font.mergeFonts("sources/bi.sfd")
font.mergeFonts("sources/sfup.sfd")
font.mergeFonts("sources/sfit.sfd")
font.mergeFonts("sources/sfbf.sfd")

font.version = sys.argv[3]
font.generate(sys.argv[2], flags=("opentype"))
