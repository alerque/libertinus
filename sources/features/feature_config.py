
sfd_dir = '..'
feature_file_dir = '.'

# Font variant groups
variant_r = 'LibertinusSerif-Regular.sfd'
variant_i = 'LibertinusSerif-Italic.sfd'
variant_b = 'LibertinusSerif-Bold.sfd'
variant_bi = 'LibertinusSerif-BoldItalic.sfd'
variant_sb = 'LibertinusSerif-Semibold.sfd'
variant_sbi = 'LibertinusSerif-SemiboldItalic.sfd'
variant_dr = 'LibertinusSerifDisplay-Regular.sfd'
variant_s_r = 'LibertinusSans-Regular.sfd'
variant_s_i = 'LibertinusSans-Italic.sfd'
variant_s_b = 'LibertinusSans-Bold.sfd'

variants = {}

variants['serif'] = [ variant_r, variant_i, variant_b,
                      variant_bi, variant_sb, variant_sbi ]
variants['sans'] = [ variant_s_r, variant_s_i, variant_s_b ]

variants['sc'] = variants['serif'] + variants['sans']
variants['nosc'] = [ variant_dr ]
variants['nosans'] = variants['serif'] + variants['nosc']

variants['all'] = variants['sc'] + variants['nosc']

variants['it'] = [ variant_i, variant_bi, variant_sbi, variant_s_i ]
variants['noit'] = [ x for x in variants['all'] if x not in variants['it'] ]

# Feature file specifications 
file_spec = {}

file_spec['case'] = { 'tables' : [ ("'case' Versalformen 1", 'case_sub') ],
                       'files' : [ 'case_all.fea' ]
                    }

file_spec['contextual'] = { 'tables'   : [ ("Chaining_Substitutions 1", 'chain_sub') ],
                             'files'   : [ 'contextual_sc.fea', 'contextual_nosc.fea' ],
                             'lookups' : [ ("'frac' Contextual Chaining Substitution", 'frac_lookup'),
                                           ("'calt' Contextual Alternates", 'calt_lookup'),
                                           ("'ccmp' Contextual Chaining Substitution", 'ccmp_lookup') ]
                          }

file_spec['dhlig'] = { 'tables' : [ ("'dlig' optionale Ligaturen 1", 'dlig_sub'),
                                    ("'hlig' Historische Ligaturen 1", 'hlig_sub') ],
                        'files' : [ 'dhlig_nosans.fea', 'dhlig_sans.fea' ]
                     }

file_spec['liga'] = { 'tables' : { 'nosans' : [ ("'locl' Reverse f_i 1", 'unfi_sub'),
                                                ("'liga' Standardligaturen 1", 'liga_sub') ],
                                   'sans'   : [ ("'liga' Standardligaturen 1", 'liga_sub') ]
                                 },
                       'files' : [ 'liga_nosans.fea', 'liga_sans.fea' ],
                    }

file_spec['locl'] = { 'tables' : [ ("'locl' Localised Forms Cyrillic-1", 'cyri_sub'),
                                   ("'locl' Localised Forms for Sami-1", 'sami_sub') ],
                       'files' : [ 'locl_noit.fea', 'locl_it.fea' ]
                    }

file_spec['num'] = { 'tables' : [ ("'case' Versalformen Figures", 'case_fig'),
                                  ("'onum' Minuskelziffern 1", 'onum_sub'), 
                                  ("'lnum' Versalziffern 1", 'lnum_sub'), 
                                  ("'pnum' Proportionalziffern 1", 'pnum_sub'),
                                  ("'tnum' Tabellenziffern 1", 'tnum_sub'),
                                  ("'zero' gestrichene Null 1", 'zero_sub') ],
                      'files' : [ 'num_all.fea' ]
                   }

file_spec['sc'] = { 'tables' : [ ("'smcp' Gemeine nach Kapitaelchen i > i.sc 1", 'smcpii_sub'),
                                 ("'smcp' Gemeine nach Kapitaelchen 1", 'smcp1_sub'),
                                 ("'smcp' Gemeine nach Kapitaelchen i > idotaccent.sc", 'smcpdot_sub'),
                                 ("'c2sc' Versale nach Kapitaelchen 1", 'c2sc_sub') ],
                     'files' : [ 'sc_sc.fea' ]
                  }

file_spec['small'] = { 'tables' : [ ("'frac' Brueche 1", 'fracb_sub'),
                                    ("sups_Hochgestellte 1", 'sups_sub'),
                                    ("sinf_Tiefgestellte 1", 'sinf_sub') ],
                        'files' : [ 'small_all.fea' ]
                     }

sscv_table_sans = [ ("'ss01' Stilgruppe 1 1", 'ss01_sub'),
                    ("'ss03' Stilgruppe 3 1", 'ss03_sub'),
                    ("'ss04' Stilgruppe 4 1", 'ss04_sub'),
                    ("'ss06' Stilgruppe 6 1", 'ss06_sub'),
                    ("'ss07' Swap 'Eng' forms-1", 'ss07_sub'),
                    ("'salt' Stilistische Alternativformen 1", 'salt_sub') ]

sscv_table_nosans = sscv_table_sans + [ ("'ss02' Stilgruppe 2 1", 'ss02_sub'), 
                                        ("'ss05' Stilgruppe 5 1", 'ss05_sub') ]


file_spec['sscv'] = { 'tables' : { 'serif' : sscv_table_nosans,
                                   'nosc'  : sscv_table_nosans,
                                   'sans'  : sscv_table_sans },
                       'files' : [ 'sscv_serif.fea', 'sscv_nosc.fea', 'sscv_sans.fea' ]
                    }
