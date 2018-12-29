#!/usr/bin/env python

# SFD normalizer (discards GUI information from SFD files)
# (c) 2004, 2005 Stepan Roh (PUBLIC DOMAIN)
# (c) 2009 Alexey Kryukov
# (c) 2018 Khaled Hosny
# (c) 2018 Skef Iterum
#
# usage: ./sfdnormalize.py sfd_file(s)
#  will rewrites files in place

# changes done:
#   WinInfo - discarded
#   DisplaySize - discarded
#   AntiAlias - discarded
#   FitToEm - discarded
#   Compacted - discarded
#   GenTags - discarded
#   Flags   - discarded O (open), H (changed since last hinting - often irrelevant)
#   Refer   - changed S (selected) to N (not selected)
#   Fore, Back, SplineSet, Grid
#           - all points have 4 masked out from flags (selected)
#   ModificationTime - discarded
#   Validated - discarded
#   Empty glyph positions dropped
#   Hinting dropped

# !!! Always review changes done by this utility !!!

from __future__ import print_function

from collections import OrderedDict

import sys, re

fealines_tok = '__X_FEALINES_X__'

FONT_RE = re.compile(r"^SplineFontDB:\s(\d+\.?\d*)")
DROP_RE = re.compile(r"^(WinInfo|DisplaySize|AntiAlias|FitToEm|Compacted|GenTags|ModificationTime|DupEnc)")
SPLINESET_RE = re.compile(r"^(Fore|Back|SplineSet|Grid)\s*$")
STARTCHAR_RE = re.compile(r"^StartChar:\s*(\S+)\s*$")
ENCODING_RE = re.compile(r"^Encoding:\s*(\d+)\s+(\-?\d+)\s*(\d*)\s*$")
BITMAPFONT_RE = re.compile(r"^(BitmapFont:\s+\d+\s+)(\d+)(\s+\d+\s+\d+\s+\d+)")
BDFCHAR_RE = re.compile(r"^BDFChar:\s*(\d+)(\s+.*)$")
EMPTY_FLAGS_RE = re.compile(r"^Flags:\s*$")
DROP_FLAGS_RE = re.compile(r"^(Flags:.*?)[HO](.*)$")
SELECTED_POINT_RE = re.compile(r"(\s+[mcl]+?\s)(\d+)(\s*)$")
SELECTED_REF_RE = re.compile(r"(-?\d+\s+)S(\s+-?\d+)")
OTFFEATNAME_RE = re.compile(r"OtfFeatName:\s*'(....)'\s*(\d+)\s*(.*)$")
HINTS_RE =  re.compile(r"^[HVD]Stem2?: ")
FEASUBPOS_RE = re.compile(r"^(Position|PairPos|LCarets|Ligature|Substitution|MultipleSubs|AlternateSubs)2?:")

fealine_order = {'Position': 1, 'PairPos': 2, 'LCarets': 3, 'Ligature': 4,
                 'Substitution': 5, 'MultipleSubs': 6, 'AlternateSubs': 7 }

# The following class is used to emulate variable assignment in
# conditions: while testing if a pattern corresponds to a specific
# regular expression we also preserve the 'match' object for future use.
class RegexpProcessor:
    def test(self, cp, string):
        self.m = cp.search(string)
        return not(self.m is None)

    def match(self):
        return self.m

def clear_selected(m):
    pt = int(m.group(2)) & ~4;
    return m.group(1) + str(pt) + m.group(3)

def process_sfd_file(sfdname, outname):
    fp = open(sfdname, 'rt')
    out = open(outname, 'wt')
    fl = fp.readline()
    proc = RegexpProcessor()

    if proc.test(FONT_RE, fl) == False:
        print("%s is not a valid spline font database" % sfdname)
        return

    out.write(fl)

    curglyph = ''
    cur_gid = 0
    in_spline_set = False
    max_dec_enc = 0
    max_unicode = 0
    new_gid = 0
    in_chars = False
    in_bdf = False
    bmp_header = ()
    bdf = OrderedDict()
    glyphs = OrderedDict()
    feat_names = {}

    fl = fp.readline()
    while fl:
        if proc.test(DROP_RE, fl):
            fl = fp.readline()
            continue

        elif in_chars:
            # Cleanup glyph flags
            fl = DROP_FLAGS_RE.sub(r"\1\2", fl)
            fl = DROP_FLAGS_RE.sub(r"\1\2", fl)

            # If we have removed all previously specified glyph flags,
            # then don't output the "Flags" line for this glyph
            if proc.test(EMPTY_FLAGS_RE, fl):
                fl = fp.readline()
                continue

        if proc.test(SPLINESET_RE, fl):
            in_spline_set = True;

        elif fl.startswith("EndSplineSet"):
            in_spline_set = False;

        elif (in_spline_set):
            # Deselect selected points
            fl = SELECTED_POINT_RE.sub(clear_selected, fl)

        if fl.startswith("BeginChars:"):
            in_chars = True;

        elif fl.startswith("EndChars"):
            in_chars = False;

            out.write("BeginChars: %s %s\n" % (max_dec_enc + 1, len(glyphs)))

            for glyph in glyphs.values():
                out.write("\n")
                out.write("StartChar: %s\n" % glyph['name'])
                out.write("Encoding: %s %s %s\n" % (glyph["dec_enc"], glyph['unicode'], glyph["gid"]))

                for gl in glyph['lines']:
                    if gl.startswith("Refer: "):
                        # deselect selected references
                        gl = SELECTED_REF_RE.sub(r"\1N\2", gl)
                    elif gl.endswith(" [ddx={} ddy={} ddh={} ddv={}]\n"):
                        gl = gl.replace(" [ddx={} ddy={} ddh={} ddv={}]", "")
                    elif gl == fealines_tok:
                        for (flt, fll) in sorted(glyph['fealines']):
                            out.write(fll)
                        continue
                    elif proc.test(HINTS_RE, gl):
                        continue
                    elif gl.startswith("Validated:"):
                        continue
                    out.write(gl)
                out.write("EndChar\n")

            out.write("EndChars\n")

        elif proc.test(STARTCHAR_RE, fl):
            curglyph = proc.match().group(1)
            glyph = { 'name' : curglyph, 'lines' : [] , 'fealines': [] }

            while curglyph in glyphs:
                curglyph = curglyph + '#'

            glyphs[curglyph] = glyph

        elif proc.test(ENCODING_RE, fl):
            dec_enc = int(proc.match().group(1))
            unicode_enc = int(proc.match().group(2))
            gid = int(proc.match().group(3))

            max_dec_enc = max(max_dec_enc, dec_enc)
            max_unicode = max(max_unicode, unicode_enc)

            glyphs[curglyph]['dec_enc'] = dec_enc;
            glyphs[curglyph]['unicode'] = unicode_enc;
            glyphs[curglyph]['gid'] = gid;

        elif proc.test(FEASUBPOS_RE, fl):
            fea_type = proc.match().group(1)
            if len(glyphs[curglyph]['fealines']) == 0:
                glyphs[curglyph]['lines'].append(fealines_tok)
            glyphs[curglyph]['fealines'].append((fealine_order.get(fea_type, 0), fl))

        elif fl.startswith("EndChar"):
            curglyph = '';

        elif proc.test(BITMAPFONT_RE, fl):
            in_bdf = True;
            bdf_header = (proc.match().group(1), str(len(glyphs)), proc.match().group(3))

        elif fl.startswith("EndBitmapFont"):
            out.write(''.join(bdf_header) + "\n")
            max_bdf = int(bdf_header[1])
            for gid in range(0, max_bdf):
                if gid in bdf:
                    for bdfl in bdf[gid]['lines']:
                        out.write(bdfl)

            out.write("EndBitmapFont\n")
            in_bdf = False;
            bdf = {}
            bdf_header = ()

        elif proc.test(BDFCHAR_RE, fl):
            cur_gid = int(proc.match().group(1))
            bdf_char = { 'gid' : cur_gid, 'lines' : [] }
            bdf_char['lines'].append("BDFChar: " + str(cur_gid) +  proc.match().group(2) + "\n")
            bdf[cur_gid] = bdf_char

        elif proc.test(OTFFEATNAME_RE, fl):
            while proc.test(OTFFEATNAME_RE, fl):
                tag, lang, name = proc.match().groups()
                feat_names[(tag, lang)] = name
                fl = fp.readline()
            for feat in sorted(feat_names):
                out.write("OtfFeatName: '%s' %s %s\n" % (feat[0], feat[1], feat_names[feat]))
            continue

        else:
            if not in_chars and not in_bdf:
                out.write(fl);
            elif in_chars and curglyph != '':
                glyphs[curglyph]['lines'].append(fl)
            elif in_bdf:
                bdf[cur_gid]['lines'].append(fl)

        fl = fp.readline()

    fp.close()
    out.close()

# Program entry point
argc = len(sys.argv)
if argc > 2:
    process_sfd_file(sys.argv[1], sys.argv[2])
else:
    print("Usage: sfdnormalize.py input_file.sfd output_file.sfd")

