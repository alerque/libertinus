# Contributing

The source files are under the `sources` subdirectory.
The `.sfd` files are FontForge source font format and should be edited with [FontForge][fontforge].
The `.fea` files are [OpenType feature files][fea] and should be edited by a plain text editor.

To build the fonts locally, you will need to install [Fontship][fontship].
Regenerate the fonts at any time using:

    fontship make

A remote CI runner will also automatically run `fontship` for all PRs on this repository, so in some cases you may not need to install it at all.
You can even download the fonts it builds each time it runs a check.
Hovever this is cumbersome for actual font development and we recomend checking your work with local feedback.
To

Note that FontForge adds unnessesary clutter to its source files on save that **must** be removed before committing.
After modifying the `.sfd` files, and before committing the changes, you can automatically clean them up with:

    fontship make normalize

[fontship]: https://github.com/theleagueof/fontship
[fontforge]: https://fontforge.org
[fea]: https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html
