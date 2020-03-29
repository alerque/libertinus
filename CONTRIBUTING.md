Contributing
------------

To build the fonts, you need [GNU Make][make] and [Python 3.6+][python], as well
as [a few Python packages](requirements.txt). The cleanest way to install the
Python dependencies is to use a [virtual environment][venv]:

    python3 -m venv libertinus-env
    . libertinus-env/bin/activate
    pip install -r requirements.txt

The source files are under the `sources` subdirectory. The `.sfd` files are
FontForge source font format and should be edited with [FontForge][fontforge].
The `.fea` files are [OpenType feature files][fea] and should be edited by a
plain text editor.

After modifying the `.sfd` files, and before committing the changes, they must
be normalized with:

    make normalize

We keep the generated fonts under version control, so the last step is to run:

    make

Which will build the `.otf` font files that should be committed as well.

Fonts must be generated for each commit that changes the source files. The
build tools are smart enough to not change the binary fonts if the sources were
not changed.

[make]: https://www.gnu.org/software/make/
[python]: https://www.python.org
[venv]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
[fontforge]: https://fontforge.org
[fea]: https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html
