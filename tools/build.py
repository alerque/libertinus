import fontforge
import argparse
from datetime import date

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-v", "--version", required=True)
parser.add_argument("-f", "--feature-file", required=False)
parser.add_argument("-c", "--copyright-file", required=True, type=argparse.FileType('r'))

args = parser.parse_args()

font = fontforge.open(args.input)

if args.feature_file:
    font.mergeFeature(args.feature_file)

copyright = args.copyright_file.read()

font.version = args.version
font.copyright = copyright.rstrip() % date.today().year
font.selection.all()
font.autoHint()
font.generate(args.output, flags=("opentype"))
