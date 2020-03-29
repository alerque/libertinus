Contributing
------------

To build the fonts, you need GNU Make, and Python 3.6+, and a few Python
packages. To install Python packages. The cleanest way to install the Python
dependencies is to use a virtual environment:

    python3 -m venv env
    . env/bin/activate
    pip install -r requirements.txt

The source files are under the `sources` subdirectory. The `.sfd` files are
FontForge source font format and should be edited with FontForge. The `.fea`
files are Adobe feature files and should be edited by a plain text editor.

After modifying the SFD files, they must be normalized before committing them
with:

    make normalize

We keep the generated fonts under version control, so the last step is to run:

    make

Which will build the font file that should be committed as well.

Fonts must be generated for each commit that changes the source files. The
build tools are smart enough to not change the binary fonts if the sources were
not changed.
