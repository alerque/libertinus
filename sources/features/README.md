# OpenType Adobe Feature File Support

The FontForge interfaces for OpenType feature tables leave much to be desired.
It is easy to “merge” an Adobe-syntax feature file into a font via the GUI or
Python, but unless one starts from scratch every time the control over subtable
order is almost nonexistent. Given that that order is very important, this is
primarily helpful for subtables that can be processed last (where new Lookups
are added by `mergeFeature`). 

Alternatively, one can try to construct new tables via script, which gives some
control over relative order. But that process is picky and likely to lead to
errors, particularly in the “language strings” at the Lookup-level.

As a work-around for these problems one can instead replace the contents of an
existing sub-table with one specified in a feature file using the following
procedure:

1. Go through every glyph and use `removePosSub` with the name of the existing
   subtable. At the end of this process the subtable will be empty.

2. Use `mergeFeature` to merge in the feature file with the new table data.

3. Use `mergeLookups` to move the just-added subtable from the (minimal) lookup
   created when the file was merged to the Lookup of the existing subtable.
   This also deletes the minimal lookup.

4. Use `mergeLookupSubtables` to move the contents of the added subtable into
   the existing table and to delete the added subtable.

Contextual substitutions have to be handled a bit differently, because FontForge
maintains one subtable per "rule". The data are also stored in the font headers
rather than in the individual glyph entries. So instead of replacing the
subtable contents for contextual lookups, one can delete all the subtables and
merge in those created by loading a feature file with chaining rules. 

These processes are particularly handy because they don't otherwise change the
metadata of the existing table or its enclosing `Lookup`. 

The files in this directory support this style of substitution table update.
`reload_features.py` is the python script that does the work. It executes
`feature_config.py`, which gives the mappings between SFD and feature file, and
feature file lookups and SFD subtable names. The script can be run with any
of these feature type specifiers:

1. "case": subtable "'case' Versalformen 1"
2. "contextual": subtable "Chaining_Substitutions 1" and Contextual Lookups for
   'frac', 'calt' and 'ccmp' (the latter two of which reference the subtable
   for their substitutions).
3. "dhlig": subtables "'dlig' optionale Ligaturen 1" and "'hlig'" Historische
   Ligaturen 1"
4. "liga": subtables "'liga' Standardligaturen 1" and "'locl' Reverse f_i 1"
   (these correspond to tables that were previously specified in "common.fea").
5. "locl": subtables "'locl' Localised Forms Cyrillic-1" and "'locl' Localised
   Forms for Sami-1".
6. "num": subtables "'case' Versalformen Figures", "'onum' Minuskelziffern 1",
   "'lnum' Versalziffern 1", "'pnum' Proportionalziffern 1", "'tnum'
   Tabellenziffern 1", and "'zero' gestrichene Null 1".
7. "sc": subtables "'smcp' Gemeine nach Kapitaelchen i > i.sc 1", "'smcp'
   Gemeine nach Kapitaelchen 1", and "'smcp' Gemeine nach Kapitaelchen
   i > idotaccent.sc".
8. "small": subtables "'frac' Brueche 1", "sups_Hochgestellte 1", and
   "sinf_Tiefgestellte 1".
9. "sscv": subtables "'ss01' Stilgruppe 1 1", "'ss02' Stilgruppe 2 1", "'ss03'
   Stilgruppe 3 1", "'ss04' Stilgruppe 4 1", "'ss05' Stilgruppe 5 1", "'ss06'
   Stilgruppe 6 1", "'ss07' Swap 'Eng' forms-1", and "'salt' Stilistische
   Alternativformen 1",

Together these contextual lookups and subtables represent all GSUB data in the
"main" font files (other than Mono, which has few features, and Math, which is
waiting on a systematic integration with Serif-Regular) with two exceptions:

1. The experimental support for combining characters over superior letters in
   Serif-Regular.

2. The partially implemented Elvish (!) variant of Sans-Bold, which is mapped
   to ss05. (I expect to propose removing this mapping and deleting the
   pure-reference `.elb` glyphs, leaving the modified characters unmapped in
   the source for anyone they might interest.) 

Note that instead of reloading the subtables and contextual lookups, one can also just remove their contents by running:

    ./reload_features.py --empty locl

instead of

    ./reload_features.py locl

This is primarily useful for hand-editing the `Lookup` lines in an SFD file and
not having to worry about changing the names of individual subtable entries to
match.

# Notes on "How It All Works"

Rather than producing a lot of documentation I have tried to keep the magnitude
of this interface and implementation small enough to comprehend by inspection. It is
quick and dirty but does the job. Still, here are some observations that might speed
that inspection:

1. At the top of `feature_config.py` the relevant SFD files are organized into
   groups like 'all', 'sans'/'nosans', 'sc'/'nosc' and so forth. These groups
   correspond to the string after the underscore and before the period in the
   `.fea` files. A file with that group will be merged into the corresponding
   SFD files only. 

2. The feature types listed in the last section are configured by adding
   `file_spec` entries in `feature_config.py`. Each will have a list of `files`
   and a `tables` value. If the latter is a list, the tuples in the list will
   be used for every file. If it is a dict, the tuples will be picked by group
   name. The first entry in the tuple should be the name of a *subtable* in the
   SFD. The second entry should be the name of a *lookup* in the feature file. 

3. `file_spec` entries can also have a `lookups` value. This is similar to
   a `tables` value except the first tuple value should be the name of
   a *lookup* in the SFD rather than a *subtable*.
