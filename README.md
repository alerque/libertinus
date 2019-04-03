[![Build Status](https://travis-ci.org/libertinus-fonts/libertinus.svg?branch=master)](https://travis-ci.org/libertinus-fonts/libertinus)

Libertinus fonts
================

***This project is in maintenance mode. Only bug reports will be considered, or
feature requests accompanied by pull requests.***

![Sample of Libertinus fonts](documentation/preview.png)

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
“[Releases](https://github.com/libertinus-fonts/libertinus/releases)” page
of the project on GitHub.

Building
--------
To build the fonts, you need GNU Make, [FontForge][1] with Python support, and
[FontTools][2]. The latest versions of FontForge and FontTools are preferred.
To load and compare GSUB features you also need the [preprocess][3] python module,
which can be installed by following the instructions on the web page or, if your
system has `pip`, with the commands:

    pip install https://github.com/doconce/preprocess/archive/master.zip

(The version of preprocess registered with `PyPi` is out of date.)

To build the fonts:

    make

To build the PDF samples you need [fntsample][4], and then:

    make doc

Contributing
------------
The source files are under the `sources` subdirectory. The `.sfd` files are
FontForge source font format and should be edited with FontForge. The `.fea`
files are Adobe feature files and should be edited by a plain text editor.

After modifying the SFD files, they should be normalized with:

    make normalize

(Make sure to save a copy of the SFD files before running this tool. The
simplest way is to commit the SFD files, normalize, check the diffs and verify
they are OK, then `git commit --amend` the changes).

We keep the generated fonts under version control, so the last step is to run
`make` and commit the modified sources and the generated fonts.

Generating the fonts for each commit is preferred, but not absolutely required.

[1]: https://fontforge.github.io
[2]: https://github.com/fonttools/fonttools
[3]: https://github.com/doconce/preprocess
[4]: https://github.com/eugmes/fntsample
