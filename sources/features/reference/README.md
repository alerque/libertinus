# “Reference” Feature Files

The FontForge interfaces for OpenType feature tables leave much to be
desired. It is easy to “merge” an Adobe-syntax feature file into a 
font via the GUI or Python, but in the case of the latter the control
over subtable order is almost nonexistent. Given that that order is
very important, this is primarily helpful for subtables that can be
processed last (where new Lookups are added by `mergeFeature`). 

Alternatively, one can try to construct new tables via script, which gives some
control over relative order. But that process is picky and likely to lead to
errors, particularly in the “language strings” at the Lookup-level.

All this said, there is a decent work-around by which one can replace the
contents of an existing sub-table with that of a subtable in a feature file:

1. Go through every glyph and use `removePosSub` with the name of the existing
   subtable. At the end of this process the subtable will be empty.

2. Use `mergeFeature` to merge in the feature file with the new table data.

3. Use `mergeLookups` to move the just-added subtable from the (minimal) lookup
   created when the file was merged to the Lookup of the existing subtable.
   This also deletes the minimal lookup.

4. Use `mergeLookupSubtables` to move the contents of the added subtable into
   the existing table and to delete the added subtable.

This process is particularly handy because it doesn't otherwise change the
metadata of the existing table or its enclosing Lookup. 

The files in this directory support this algorithm. At the time of writing only
the five numeral-specific features (`onum`, `lnum`, `pnum`, `tnum`, and
`zero`), and an additional figure-specific `case` subtable are implemented.
However, it would be easy enough to support wide swaths of the font's OpenType
feature information this way. The lookup order would still be determined by the
order in the font files, which might be changed accidentally but is easy enough
to change back either with the GUI or editing the `.sfd` file directly.

Rather than use this process every time the fonts are built, however, it
seems preferable (for now, at least) to just leave the information in the
font and change it by hand as necessary. So that is the intended use of the
files in this directory: When a subtable needs to be changed it can be changed
in the corresponding feature file, and then the script can be run to move the
change into the font files.
