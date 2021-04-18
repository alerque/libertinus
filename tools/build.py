import argparse
import datetime
import ufo2ft
import ufoLib2

from fontTools import subset
from io import StringIO
from pcpp.preprocessor import Preprocessor
from sfdLib.parser import SFDParser, CATEGORIES_KEY, MATH_KEY


class Font:
    def __init__(self, filename, features):
        self._font = font = ufoLib2.Font(validate=False)

        parser = SFDParser(filename, font, ufo_anchors=False,
            ufo_kerning=False, minimal=True)
        parser.parse()

        if features:
            preprocessor = Preprocessor()
            for d in ("italic", "sans", "display", "math"):
                if d in filename.lower():
                    preprocessor.define(d.upper())
            with open(features) as f:
                preprocessor.parse(f)
            feafile = StringIO()
            preprocessor.write(feafile)
            feafile.write(font.features.text)
            font.features.text = feafile.getvalue()

    def _update_metadata(self):
        font = self._font
        info = font.info

        year = datetime.date.today().year
        info.copyright = (u"Copyright © 2012-%s " % year +
                          u"The Libertinus Project Authors.")
        info.openTypeNameManufacturerURL = "https://github.com/alerque/libertinus"

    def _draw_over_under_line(self, name, widths):
        font = self._font
        bbox = font[name].getBounds(font)
        pos = bbox[1]
        height = bbox[-1] - bbox[1]

        for width in sorted(widths):
            glyph = font.newGlyph(f"{name}.{width}")
            glyph.width = 0
            glyph.lib[CATEGORIES_KEY] = "mark"

            pen = glyph.getPen()
            pen.moveTo((-25 - width, pos))
            pen.lineTo((-25 - width, pos + height))
            pen.lineTo((25, pos + height))
            pen.lineTo((25, pos))
            pen.closePath()

    def _make_over_under_line(self):
        font = self._font
        minwidth = 50

        bases = [n for n in ("uni0305", "uni0332") if n in font]
        if not bases:
            return

        # Collect glyphs grouped by their widths rounded by minwidth, we will
        # use them to decide the widths of over/underline glyphs we will draw
        widths = {}
        for glyph in font:
            glyphclass = glyph.lib.get(CATEGORIES_KEY)
            if glyphclass != 'mark' and glyph.width > 0:
                width = round(glyph.width / minwidth) * minwidth
                width = max(width, minwidth)
                if width not in widths:
                    widths[width] = []
                widths[width].append(glyph.name)

        if len(widths) == 1:
            return

        for name in bases:
            self._draw_over_under_line(name, widths)

        fea = []
        fea.append("feature mark {")
        fea.append(f"  @OverSet = [{' '.join(bases)}];")
        fea.append("  lookupflag UseMarkFilteringSet @OverSet;")
        for width in sorted(widths):
            # For each width group we create an over/underline glyph with the
            # same width, and add a contextual substitution lookup to use it
            # when an over/underline follows any glyph in this group
            replacements = ['%s.%d' % (name, width) for name in bases]
            fea.append("  sub [%s] [%s]' by [%s];" % (" ".join(widths[width]),
                                                      " ".join(bases),
                                                      " ".join(replacements)))
        fea.append("} mark;")

        self._font.features.text += "\n".join(fea)

    def _post_process(self, otf):
        font = self._font
        gdef = otf["GDEF"].table
        classdef = gdef.GlyphClassDef.classDefs
        for glyph in font:
            if glyph.lib.get(CATEGORIES_KEY) == "mark":
                classdef[glyph.name] = 3

        constants = font.lib.get(MATH_KEY)
        if constants:
            from fontTools.ttLib import newTable
            from fontTools.ttLib.tables import otTables
            from fontTools.otlLib import builder as otl

            glyphMap = {n: i for i, n in enumerate(font.glyphOrder)}
            table = otTables.MATH()
            table.Version = 0x00010000
            table.MathConstants = otTables.MathConstants()
            for c in constants:
                if c == "MinConnectorOverlap":
                    continue
                v = constants[c]
                if c not in ("ScriptPercentScaleDown",
                        "ScriptScriptPercentScaleDown",
                        "DelimitedSubFormulaMinHeight",
                        "DisplayOperatorMinHeight",
                        "RadicalDegreeBottomRaisePercent"):
                    vr = otTables.MathValueRecord()
                    vr.Value = v
                    v = vr
                setattr(table.MathConstants, c, v)
            extended = set()
            italic = {}
            accent = {}
            vvars = {}
            hvars = {}
            vcomp = {}
            hcomp = {}
            for glyph in font:
                math = glyph.lib.get(MATH_KEY)
                if math:
                    if "IsExtendedShape" in math:
                        extended.add(glyph.name)
                    if "ItalicCorrection" in math:
                        italic[glyph.name] = otTables.MathValueRecord()
                        italic[glyph.name].Value = math["ItalicCorrection"]
                    if "TopAccentHorizontal" in math:
                        accent[glyph.name] = otTables.MathValueRecord()
                        accent[glyph.name].Value = math["TopAccentHorizontal"]
                    if "GlyphVariantsVertical" in math:
                        vvars[glyph.name] = math["GlyphVariantsVertical"]
                        if "GlyphCompositionVertical" in math:
                            vcomp[glyph.name] = math["GlyphCompositionVertical"]
                    if "GlyphVariantsHorizontal" in math:
                        hvars[glyph.name] = math["GlyphVariantsHorizontal"]
                        if "GlyphCompositionHorizontal" in math:
                            hcomp[glyph.name] = math["GlyphCompositionHorizontal"]

            table.MathGlyphInfo = otTables.MathGlyphInfo()
            table.MathGlyphInfo.populateDefaults()

            coverage = otl.buildCoverage(italic.keys(), glyphMap)
            table.MathGlyphInfo.MathItalicsCorrectionInfo = otTables.MathItalicsCorrectionInfo()
            table.MathGlyphInfo.MathItalicsCorrectionInfo.Coverage = coverage
            table.MathGlyphInfo.MathItalicsCorrectionInfo.ItalicsCorrection = [italic[n] for n in coverage.glyphs]

            coverage = otl.buildCoverage(accent.keys(), glyphMap)
            table.MathGlyphInfo.MathTopAccentAttachment = otTables.MathTopAccentAttachment()
            table.MathGlyphInfo.MathTopAccentAttachment.TopAccentCoverage = coverage
            table.MathGlyphInfo.MathTopAccentAttachment.TopAccentAttachment = [accent[n] for n in coverage.glyphs]

            table.MathGlyphInfo.ExtendedShapeCoverage = otl.buildCoverage(extended, glyphMap)

            table.MathVariants = otTables.MathVariants()
            table.MathVariants.MinConnectorOverlap = constants["MinConnectorOverlap"]

            coverage = otl.buildCoverage(vvars.keys(), glyphMap)
            table.MathVariants.VertGlyphCoverage = coverage
            table.MathVariants.VertGlyphConstruction = []
            for name in coverage.glyphs:
                variants = vvars[name]
                construction = otTables.MathGlyphConstruction()
                construction.populateDefaults()
                construction.VariantCount = len(variants)
                construction.MathGlyphVariantRecord = []
                for variant in variants:
                    bbox = font[variant].getBounds(font)
                    record = otTables.MathGlyphVariantRecord()
                    record.VariantGlyph = variant
                    record.AdvanceMeasurement = int(bbox[-1] - bbox[1] + 1)
                    construction.MathGlyphVariantRecord.append(record)
                if name in vcomp:
                    construction.GlyphAssembly = otTables.GlyphAssembly()
                    construction.GlyphAssembly.ItalicsCorrection = otTables.MathValueRecord()
                    construction.GlyphAssembly.ItalicsCorrection.Value = 0
                    construction.GlyphAssembly.PartRecords = []
                    for comp in vcomp[name]:
                        record = otTables.GlyphPartRecord()
                        record.glyph = comp[0]
                        f, s, e, a = [int(v) for v in comp[1].split(",")]
                        record.StartConnectorLength = s
                        record.EndConnectorLength = e
                        record.FullAdvance = a
                        record.PartFlags = f
                        construction.GlyphAssembly.PartRecords.append(record)
                table.MathVariants.VertGlyphConstruction.append(construction)

            coverage = otl.buildCoverage(hvars.keys(), glyphMap)
            table.MathVariants.HorizGlyphCoverage = coverage
            table.MathVariants.HorizGlyphConstruction = []
            for name in coverage.glyphs:
                variants = hvars[name]
                construction = otTables.MathGlyphConstruction()
                construction.populateDefaults()
                construction.VariantCount = len(variants)
                construction.MathGlyphVariantRecord = []
                for variant in variants:
                    bbox = font[variant].getBounds(font)
                    record = otTables.MathGlyphVariantRecord()
                    record.VariantGlyph = variant
                    record.AdvanceMeasurement = int(bbox[-2] - bbox[0] + 1)
                    construction.MathGlyphVariantRecord.append(record)
                if name in hcomp:
                    construction.GlyphAssembly = otTables.GlyphAssembly()
                    construction.GlyphAssembly.ItalicsCorrection = otTables.MathValueRecord()
                    construction.GlyphAssembly.ItalicsCorrection.Value = 0
                    construction.GlyphAssembly.PartRecords = []
                    for comp in hcomp[name]:
                        record = otTables.GlyphPartRecord()
                        record.glyph = comp[0]
                        f, s, e, a = [int(v) for v in comp[1].split(",")]
                        record.StartConnectorLength = s
                        record.EndConnectorLength = e
                        record.FullAdvance = a
                        record.PartFlags = f
                        construction.GlyphAssembly.PartRecords.append(record)
                table.MathVariants.HorizGlyphConstruction.append(construction)


            otf["MATH"] = newTable("MATH")
            otf["MATH"].table = table

    def _prune(self, otf):
        options = subset.Options()
        options.set(layout_features='*', name_IDs='*', notdef_outline=True,
            recalc_average_width=True, recalc_bounds=True)
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=otf['cmap'].getBestCmap().keys())
        subsetter.subset(otf)

    def generate(self, output):
        self._update_metadata()
        self._make_over_under_line()
        otf = ufo2ft.compileOTF(self._font, inplace=True, optimizeCFF=0,
            removeOverlaps=True, overlapsBackend="pathops", featureWriters=[])
        self._post_process(otf)
        self._prune(otf)
        otf.save(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("-f", "--feature-file", required=False)

    args = parser.parse_args()
    font = Font(args.input, args.feature_file)
    font.generate(args.output)


if __name__ == "__main__":
    main()
