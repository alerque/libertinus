#!/usr/bin/env python

import fontforge

variants = [ 'Serif-Bold', 'Serif-BoldItalic', 'Serif-Italic', 'Serif-Regular', 
              'Serif-Semibold', 'Serif-SemiboldItalic', 'SerifDisplay-Regular' ]

tabletups = [ ("'onum' Minuskelziffern 1", 'onum_sub'), 
              ("'lnum' Versalziffern 1", 'lnum_sub'), 
              ("'pnum' Proportionalziffern 1", 'pnum_sub'),
              ("'tnum' Tabellenziffern 1", 'tnum_sub'),
              ("'zero' gestrichene Null 1", 'zero_sub'),
              ("'case' Versalformen Figures", 'case_fig') ]

feafile = 'num.fea'

for v in variants:
    print(v)
    ff = fontforge.open('../../Libertinus' + v + '.sfd')
    # Remove existing entries from tables
    for g in ff.glyphs():
        for etab, ntab in tabletups:
            ps = g.getPosSub(etab)
            if len(ps) > 0 and len(ps[0]) > 0 and ps[0][0] == etab:
                g.removePosSub(etab)

    # merge in the replacement feature file
    ff.mergeFeature(feafile)
    for etab, ntab in tabletups:
        el = ff.getLookupOfSubtable(etab)
        nl = ff.getLookupInfo(ntab)
        # Merge the added lookup into the existing one
        ff.mergeLookups(el, ntab)
        # Merge the entries of the added subtable into the (now empty) existing one
        ff.mergeLookupSubtables(etab, ntab + ' subtable')

    ff.save()
