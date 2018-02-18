Libertinus fonts
================

Libertinus fonts is a fork of the Linux Libertine and Linux Biolinum fonts that
started as an OpenType math companion of the Libertine font family, but grown
as a full fork to address some of the bugs in the fonts.

Libertinus is forked from 5.3.0 (2012-07-02) release of Linux Libertine fonts.

The family consists of:

* Libertinus Serif: forked from *Linux Libertine*.
* Libertinus Sans: forked from *Linux Biolinum*.
* Libertinus Mono: forked from *Linux Libertine Mono*.
* Libertinus Math: an OpenType math font for use in OpenType math-capable
  applications like LuaTeX, XeTeX or MS Word 2007+.

Libertinus fonts are available under the terms of Open Font License version
1.1.

Building
--------
To build the fonts you need GNU Make, [FontForge][1] with Python support, and
[FontTools][2], latest versions of both are preferred.

To build the PDF samples you need [fntsample][3] and, optionally, [mutool][4].

To build the fonts:

    make

To build the PDF samples:

    make doc

Contributing
------------
The fonts should be edited with FontForge, and the SFD files should be
normalized with `tools/sfdnormalize.py` (make sure to save a copy of the SFD
files before running this tool, the simplest way is to commit the SFD files,
run `tools/sfdnormalize.py` check the diffs and verify they are OK, then `git
commit --ammend` the changes).

Generating the fonts for each commit is preferred, but not absolutely required.

[1]: https://fontforge.github.io
[2]: https://github.com/fonttools/fonttools
[3]: https://github.com/eugmes/fntsample
[4]: https://mupdf.com/
