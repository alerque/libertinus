# Standard OpenType Font Features

Libertinus supports several OpenType features.
Some are enabled by default (`-`) others have to be opted in (`+`).

-   Small Caps: `+smcp` and `+c2sc`
-   Ligatures and Contextual Alternates: `-liga`, `+hlig`, `+dlig`; `-calt`
-   Kerning: `-kern`
-   Capital Spacing: `+cpsp`, `case`
-   Slashed zero: `+zero`
-   Numerals: `-tnum`, `+pnum`, `-lnum`, `+onum`, `+pnum+onum`
-   Vulgar fractions: `+frac`
-   Subscripts and Superscripts: `+sinf`, `+sups`
-   Diacritic marks: `-mark`, `-mkmk`
-   Stylistic alternates: `+salt`

Most of these can be accessed by high-level CSS properties or values 
and by GUI controls in DTP software.

## Cased forms: `+case`

All digits and some punctuation characters (i.e. parentheses, guillemets and hyphen) 
use shapes that better fit with all-uppercase text (`.cap` or `.sc`).

## Standard ligatures: `-liga`

In serif faces, 
the Latin lowercase letter sequences *ſſ*, *ſſi*, *ſſj*, *ſſk*, *ſſl*, *ſh*, *ſi*, *ſj*, *ſl*, *ſs*, *ſt*, *ff*, *ffh*, *ffi*, *ffj*, *ffk*, *ffl*, *fh*, *fi*, *fj*, *fk*, *fl*, *ft* 
form default ligatures.

In sans-serif faces, 
only the Latin lowercase letter sequences *ff* (also if the second one has a shortened head) and *ft* 
form default ligatures.

The related feature `clig` is not used.

The respective CSS property is `font-variant-ligatures` with the value `common-ligatures` (or `no-common-ligatures`).

## Discretionary and Historical Ligatures: `+dlig`, `+hlig`

The only historical ligatures supported are Latin lowercase *st* and *ct* in all faces.

In all faces, 
Latin lowercase letter sequences *tt* and *tz* 
form discretionary ligatures.
Only in serif faces (i.e. non-sans-serif), 
Latin letter sequences *Th*, *ck* and *ch* 
also form discretionary ligatures.
These can all be manually forced by using ZWJ (U+200D) between letters when just the default feature `liga` is active.

The respective CSS property is `font-variant-ligatures` with the values `discretionary-ligatures` and `historical-ligatures`.

## Contextual alternates: `-calt`

In all faces, 
the Latin capital and small-capital letter *Q* gains a long tail if followed by either lowercase or small-capital letter *u* or *v*.

The Latin lowercase letter *f*, even when part of the ligature *ff*, has a shortened head 
if followed by closing parentheses, top quotation mark, lowercase letter with ascending left leg, lowercase letter with diacritic mark above or uppercase letter not starting with a leg or stem on the left.

The related feature `clig` is not used.

The respective CSS property is `font-variant-ligatures` with the value `contextual` (or `no-contextual`).

## Localized alternates: `locl`

For Serbian and Macedonian, 
in all faces, 
the Cyrillic lowercase letter be *б* 
and in italic faces, 
the Cyrillic lowercase letters ghe *г*, gje *ѓ*, de *д*, pe *п* and te *т* 
are replaced by alternate glyphs.

For Scandinavian languages, because of preferences in Sami typography, 
the Latin uppercase letter Eng *Ŋ* uses a alternative glyph, cf. `ss07`.

For Turkic languages, 
ligatures where the Latin lowercase letter *i* is the second part are deactivated, 
i.e. *fi*, *ffi*, *ſi* and *ſſi*.
The small-capitals handling of *i* / *ı* does not depend on `locl`, but is part of `smcp` (and `c2sc`).

## Numerals: `-tnum`, `+pnum`, `-lnum`, `+onum`, `+pnum+onum`

Except for Libertinus Math, 
the standard digits can be forced to *old-style* forms (with ascenders and descenders) with `onum` (`.taboldstyle`), 
to default *lining* forms with `lnum`, 
to *proportional* forms with `pnum` (`.fitted`), 
to *tabular* (fixed-width) forms with `tnum`.
The latter two also apply to Euro *€* and Yen *¥* currency symbols and trump the other features.

The respective CSS property is `font-variant-numeric` with the values `oldstyle-nums`, `lining-nums`, `proportional-nums` and `tabular-nums`, respectively.

## Vulgar fractions: `+frac`; `subs`, `sups`; `sinf`

The same sets of inferior/subscript and superior/superscript glyphs are used for various features.

The respective CSS property for `frac` is `font-variant-numeric` with the value `diagonal-fractions`. The value `stacked-fraction` is not supported.

# Custom OpenType Font Features: Stylistic Sets

## Stylistic alternates: `+salt`

For non-sans-serif faces, 
Latin uppercase letters *J*, *K*, *R* and *W* use alternate glyphs (`.alt`).

For small-caps faces, 
Latin lowercase letters *a*, *q*, *ŋ* and *ß* use alternate glyphs (`.scalt` etc.).

In all faces, 
Latin uppercase letters *Q*, eng *Ŋ* and eszet *ẞ*, Latin lowercase letters *h*, *y* and Eszet *ß*, 
Greek lowercase letters Beta *β*, Theta *θ*, Kappa *κ* and Phi *φ*, 
Cyrillic lowercase letter Be *б* 
and the ampersand *&* use alternate glyphs, cf. `calt`, `ss03`, `ss04`, `ss06`, `ss07`, `locl`.

The respective CSS property is `font-variant-alternates` with the value `stylistic(<feature-value-name>)`.

## Stylistic Set 1 `ss01` *Low diaeresis on ‘A’, ‘E’, ‘O’*

Intended for German, the umlaut dots above the Latin capital letters *A* and *O* (*Ä*, *Ö*) are  moved further apart while the ones above *U* (*Ü*) are put closer together.

## Stylistic Set 2 `ss02` *Swashy ‘J’ ‘K’ ‘R’*

A bit more swashy, cursive look with elongated tails for Latin uppercase letter *K* and *R* and a left-hand horizontal top for *J*.
This does not apply to sans-serif faces.

## Stylistic Set 3 `ss03` *‘double s’ to two ‘s’*

All variants of German eszett (lowercase *ß*, uppercase *ẞ* and small-capital) are rendered as round-s digraphs *SS/ss* instead, very applicable to Swiss German texts.

## Stylistic Set 4 `ss04` *Upper case ‘double s’ to two ‘S’*

Only the uppercase German eszett *ẞ* is rendered as a round-s digraph *SS*; subset of `ss03`.

## Stylistic Set 5 `ss05` *Crossed ‘W’*

Latin uppercase letter *W* is rendered as a ligature of two *V*, i.e. the middle verticals are longer, as used in the Wikipedia logo.
This does not apply to sans-serif faces.

## Stylistic Set 6 `ss06` *Swash ‘&’*

The ampersand *&* is rendered as an *et* ligature.

## Stylistic Set 7 `ss07` *Swap ‘Eng’ forms*

The uppercase letter Eng *Ŋ*, i.e. an *N* with a descending tail on the right leg, uses the capital *N* glyph as its base instead of the default enlarged lowercase *n* glyph.
The localized `locl` UC Style for Sami is changed the other way around.
