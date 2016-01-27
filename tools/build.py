import fontforge
import argparse
from datetime import date
from os import path

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-v", "--version", required=True)
parser.add_argument("-f", "--feature-file", required=False)

args = parser.parse_args()

font = fontforge.open(args.input)

if args.feature_file and path.isfile(args.feature_file):
    font.mergeFeature(args.feature_file)

font.version = args.version
font.copyright = "Copyright 2003-2012 by Philipp H. Poll. Copyright 2012-%s Khaled Hosny." % date.today().year

font.appendSFNTName("English (US)", "Manufacturer", "Khaled Hosny")
font.appendSFNTName("English (US)", "Vendor URL", "https://github.com/khaledhosny/libertinus")
font.appendSFNTName("English (US)", "License URL", "http://scripts.sil.org/OFL")
font.appendSFNTName("English (US)", "License", '\
This Font Software is licensed under the SIL Open Font License, Version 1.1. \
This Font Software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR \
CONDITIONS OF ANY KIND, either express or implied. See the SIL Open Font License \
for the specific language, permissions and limitations governing your use of \
this Font Software.')
font.os2_vendor = "BLQ "

font.selection.all()
font.autoHint()
font.generate(args.output, flags=("opentype", "no-mac-names"))
