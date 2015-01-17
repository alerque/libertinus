import fontforge
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-v", "--version", required=True)
parser.add_argument("-f", "--feature-file", required=False)

args = parser.parse_args()

font = fontforge.open(args.input)

if args.feature_file:
    font.mergeFeature(args.feature_file)

font.version = args.version
font.selection.all()
font.autoHint()
font.generate(args.output, flags=("opentype"))
