import fontforge
import sys

font = fontforge.open(sys.argv[1])
subs = {}
langsyms = set()

for lookup in font.gsub_lookups:
    info = font.getLookupInfo(lookup)
    skip = False
    for fea in info[2]:
        if fea[0] == "aalt":
            font.removeLookup(lookup)
            skip = True
        else:
            langsyms.update(fea[1])
    if info[0] in ("gsub_single", "gsub_alternate") and not skip:
        for subtable in font.getLookupSubtables(lookup):
            for glyph in font.glyphs():
                if glyph.unicode == -1:
                    continue
                for sub in glyph.getPosSub(subtable):
                    if glyph.glyphname not in subs:
                        subs[glyph.glyphname] = set()
                    subs[glyph.glyphname].update(sub[2:])

langstr = ""
for script, langs in langsyms:
    for lang in langs:
        langstr += "languagesystem %s %s;\n" % (script, lang)
featstr = ""
for name in subs:
    featstr += "  sub %s from [%s];\n" % (name, " ".join([sub for sub in sorted(subs[name])]))
aalt = """
%s
feature aalt {
%s
} aalt;""" % (langstr, featstr)

font.mergeFeatureString(aalt)
font.save()
