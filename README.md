[![Build Status](https://travis-ci.org/alif-type/libertinus.svg?branch=master)](https://travis-ci.org/alif-type/libertinus)

Libertinus fonts
================

![Sample of Libertinus fonts](documentation/preview.svg)

***This project is in maintenance mode. Only bug reports will be considered, or
feature requests accompanied by pull requests.***

Libertinus fonts is a fork of the Linux Libertine and Linux Biolinum fonts that
started as an OpenType math companion of the Libertine font family. It has grown
to a full fork to address some of the bugs in the fonts. Thanks to Frédéric
Wang for coming up with the name Libertinus.

Libertinus was forked from the 5.3.0 (2012-07-02) release of Linux Libertine fonts.

The family consists of:

* Libertinus Serif: forked from *Linux Libertine*.
* Libertinus Sans: forked from *Linux Biolinum*.
* Libertinus Mono: forked from *Linux Libertine Mono*.
* Libertinus Math: an OpenType math font for use in OpenType math-capable
  applications (like LuaTeX, XeTeX or MS Word 2007+).

Libertinus fonts are available under the terms of the Open Font License version
1.1.

A zip file containing the font files can be downloaded from the 
“[Releases](https://github.com/alif-type/libertinus/releases)” page
of the project on GitHub.

Building
--------
To build the fonts, you need GNU Make, [FontForge][1] with Python support, the
[FontTools][2] Python module, and the [pcpp][3] Python module. The latest
versions of FontForge and FontTools are preferred.

To build the fonts:

    make

[1]: https://fontforge.github.io
[2]: https://github.com/fonttools/fonttools
[3]: https://github.com/ned14/pcpp
