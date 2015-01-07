import fontforge
import sys

font = fontforge.open(sys.argv[3])

font.version = sys.argv[2]
font.selection.all()
font.autoHint()
font.generate(sys.argv[1], flags=("opentype"))
