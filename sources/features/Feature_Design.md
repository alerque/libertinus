# Libertinus OpenType GSUB Feature Design

This brief document is a placeholder for a description of OpenType feature
support in Libertinus. For now it describes the process by which that support
was standardized across the Serif and Sans faces. 

The first and most important aspect of that standardization is that
Serif-Regular served as the "reference". It is therefore the least affected by
the changes, although it too is slightly reorganized:

1. `smcp` was moved after `frac`, `sups`, and `sinf` (this change relates to
   potential future support for smallcaps figures. As it was the tables had no
   substantial interactions.)
2. `salt` is now an alternatives table rather than a single substitution table
3. The `ssNN` subtable names were standardized.
4. `case` was moved up to right after `sinf` and substantially reorganized.
5. 'liga' was added back in as a `Lookup` entry (instead of being loaded from
   `common.fea` before generation), along with a `locl Lookup` for backing out
   ligatures in some language systems. 
6. Various support tables (e.g. `Substitution cap-Accents`) were merged into
   a common `Chaining_substitutions` table. 
7. `'sinf' Tiefgestellte` was renamed `sinf_Tiefgestellte` and `'sups'
   Hochgestellte` was renamed `sups_Hochgestellte` so that they can be
   referenced directly in feature files. 

The other main fonts now duplicate the naming and ordering of the Serif-Regular
`Lookup`s. Not every font has every `Lookup` or subtable. SerifDisplay-Regular,
for example, lacks any `smcp` `Lookup`s, and the Sans fonts have no `ss02` or
`ss05`. But the overall scheme is similar. 

Most of the work in standardizing the features involved adding missing alternate
glyphs. However, that list is outside the scope of this document. The git history
is probably the best reference for that information. 
