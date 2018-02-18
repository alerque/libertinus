#!/usr/bin/env python

# SFD normalizer (discards GUI information from SFD files)
# (c) 2004, 2005 Stepan Roh (PUBLIC DOMAIN)
# (c) 2009 Alexey Kryukov
# (c) 2018 Khaled Hosny
#
# usage: ./sfdnormalize.py sfd_file(s)
#  will rewrites files in place

# changes done:
#   WinInfo - discarded
#   DisplaySize - discarded
#   GenTags - discarded
#   Flags   - discarded O (open), H (changed since last hinting - often irrelevant)
#   Refer   - changed S (selected) to N (not selected)
#   Fore, Back, SplineSet, Grid
#           - all points have 4 masked out from flags (selected)
#   ModificationTime - discarded

# !!! Always review changes done by this utility !!!

from __future__ import print_function

import sys, os, re, string
import fontforge

# The following class is used to emulate variable assignment in
# conditions: while testing if a pattern corresponds to a specific
# regular expression we also preserve the 'match' object for future use.
class RegexpProcessor:
    def __init__(self, m=None):
        self.m = m

    def test(self, pattern, string):
        self.m = re.search(pattern, string)
        return not(self.m is None)

    def test_special(self, pattern, string, startpos=0):
        cp = re.compile(pattern)
        self.m = cp.search(string, startpos)
        return not(self.m is None)

    def match(self):
        return self.m

def clear_selected(m):
    pt = int(m.group(2)) & ~4;
    return m.group(1) + str(pt) + m.group(3)

def process_sfd_file(sfdname):
    if not os.access(sfdname, os.R_OK):
        print("Cannot open %s", sfdname)
        return

    if not os.access(sfdname, os.W_OK) and not os.access(os.getcwd(), os.W_OK):
        print("Cannot write to %s", sfdname)
        return

    fp = open(sfdname, 'rt')
    out = []
    fl = fp.readline()
    proc = RegexpProcessor()

    if proc.test(r"^SplineFontDB:\s(\d+\.?\d*)", fl) == False:
        print("%s is not a valid spline font database", sfdname)
        return

    out.append(fl)

    curglyph = ''
    cur_gid = 0
    in_spline_set = False
    max_dec_enc = 0
    max_unicode = 0
    new_gid = 0
    in_chars = False
    in_bdf = False
    bmp_header = ()
    bdf = {}
    glyphs = {}

    fl = fp.readline()
    while fl:
        if proc.test(r"^(WinInfo|DisplaySize|GenTags|ModificationTime|DupEnc)", fl):
            fl = fp.readline()
            continue

        if not in_chars and not in_bdf:
            fl = re.sub(r"^Compacted:.*", r"Compacted: 0", fl)

        elif in_chars:
            # Cleanup glyph flags
            fl = re.sub(r"^(Flags:.*?)O(.*)$", r"\1\2", fl)
            fl = re.sub(r"^(Flags:.*?)H(.*)$", r"\1\2", fl)

            # If we have removed all previously specified glyph flags,
            # then don't output the "Flags" line for this glyph
            if proc.test(r"^Flags:\s*$", fl):
                fl = fp.readline()
                continue

        if proc.test(r"^(Fore|Back|SplineSet|Grid)\s*$", fl):
            in_spline_set = True;

        elif proc.test(r"^EndSplineSet\s*$", fl):
            in_spline_set = False;

        elif (in_spline_set):
            # Deselect selected points
            fl = re.sub(r"(\s+[mcl]+?\s)(\d+)(\s*)$", clear_selected, fl)

        if proc.test(r"^BeginChars:", fl):
            in_chars = True;

        elif proc.test(r"^EndChars\s*$", fl):
            in_chars = False;

            out.append("BeginChars: %s %s\n" % (max_dec_enc + 1, len(glyphs)))

            for glyph in glyphs.values():
                out.append("\n")
                out.append("StartChar: %s\n" % glyph['name'])
                out.append("Encoding: %s %s %s\n" % (glyph["dec_enc"], glyph['unicode'], glyph["gid"]))

                for gl in glyph['lines']:
                    if proc.test(r"^(Refer:\s*)(\d+)(.*)$", gl):
                        # deselect selected references
                        gl = re.sub(r"(\d+\s+)S(\s+\d+)", r"\1N\2", gl)
                    out.append(gl)
                out.append("EndChar\n")

            out.append("EndChars\n")

        elif proc.test(r"^StartChar:\s*(\S+)\s*$", fl):
            curglyph = proc.match().group(1)
            glyph = { 'name' : curglyph, 'lines' : [] }

            while curglyph in glyphs:
                curglyph = curglyph + '#'

            glyphs[curglyph] = glyph

        elif proc.test(r"^Encoding:\s*(\d+)\s+(\-?\d+)\s*(\d*)\s*$", fl):
            dec_enc = int(proc.match().group(1))
            unicode_enc = int(proc.match().group(2))
            gid = int(proc.match().group(3))

            max_dec_enc = max(max_dec_enc, dec_enc)
            max_unicode = max(max_unicode, unicode_enc)

            glyphs[curglyph]['dec_enc'] = dec_enc;
            glyphs[curglyph]['unicode'] = unicode_enc;
            glyphs[curglyph]['gid'] = gid;

        elif proc.test(r"^EndChar\s*$", fl):
            curglyph = '';

        elif proc.test(r"^(BitmapFont:\s+\d+\s+)(\d+)(\s+\d+\s+\d+\s+\d+)", fl):
            in_bdf = True;
            bdf_header = (proc.match().group(1), str(len(glyphs)), proc.match().group(3))

        elif proc.test(r"^EndBitmapFont\s*$", fl):
            out.append(''.join(bdf_header) + "\n")
            max_bdf = int(bdf_header[1])
            for gid in range(0, max_bdf):
                if gid in bdf:
                    for bdfl in bdf[gid]['lines']:
                        out.append(bdfl)

            out.append("EndBitmapFont\n")
            in_bdf = False;
            bdf = {}
            bdf_header = ()

        elif proc.test(r"^BDFChar:\s*(\d+)(\s+.*)$", fl):
            cur_gid = int(proc.match().group(1))
            bdf_char = { 'gid' : cur_gid, 'lines' : [] }
            bdf_char['lines'].append("BDFChar: " + str(cur_gid) +  proc.match().group(2) + "\n")
            bdf[cur_gid] = bdf_char

        else:
            if not in_chars and not in_bdf:
                out.append(fl);
            elif in_chars and curglyph != '':
                glyphs[curglyph]['lines'].append(fl)
            elif in_bdf:
                bdf[cur_gid]['lines'].append(fl)

        fl = fp.readline()

    fp.close()

    with open(sfdname, 'wt') as fp:
        fp.writelines(out)

# Program entry point
argc = len(sys.argv)
if argc > 1:
    for sfdname in sys.argv[1:]:
        process_sfd_file(sfdname)
else:
    print("Usage: sfdnormalize.py input_file.sfd")

