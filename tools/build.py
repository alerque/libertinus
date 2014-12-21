import fontforge
import sys

font = fontforge.open(sys.argv[3])

if len(sys.argv) > 4:
  for filename in sys.argv[4:-1]:
    font.mergeFonts(filename)

font.version = sys.argv[2]
font.generate(sys.argv[1], flags=("opentype"))
