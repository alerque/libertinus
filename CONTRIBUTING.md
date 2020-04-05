Contributing
------------

To build the fonts, you need [GNU Make][make] and [Python 3.6+][python], as well
as [a few Python packages](requirements.txt). The cleanest way to install the
Python dependencies is to use a [virtual environment][venv]:

    python3 -m venv libertinus-env
    . libertinus-env/bin/activate
    pip install -r requirements.txt

(There are also [optional dependencies](#optional-dependencies) which are not
required for the basic contribution flow.)

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

### Optional dependencies

The build process, besides generating the `.otf` font files, also updates the
SVG and PDF preview documents. For that, additional tools are needed: `xelatex`
from [xetex][], and `mutool` from [mupdf][] (version 1.15.0 or above). The
`make` command will emit errors if these are not present, but as long as the
font generation stages finish correctly, these errors can be ignored. However,
if you do wish to update the preview files, these tools must also be installed.

#### Linux

On most Linux distros, the `xelatex` binary is provided by the
[`texlive-xetex` package][repology-xetex], and the `mutool` binary by
[`mupdf-tools` or `mupdf`][repology-mupdf].
In Ubuntu, for example, these packages can be installed with:

    sudo apt install texlive-xetex mupdf-tools
    
**Note:** the command example above installs an unsupported version of
`mupdf-tools` in Ubuntu versions older than 19.10 (Eoan Ermine), which is the
first one that [included][ubuntu-mupdf] the 1.15.0 release of `mupdf-tools`.
If your distro has an older version, you may consider using the [Linuxbrew][]
package manager instead to install `mupdf-tools`:

    brew install mupdf-tools

#### macOS

On macOS, [Homebrew][] can be used to install `mupdf-tools`:

    brew install mupdf-tools

On the other hand, `xelatex` is not provided as a stand-alone formula. The
simplest way to obtain it is to install the [basictex][] cask, and then link
the `xelatex` binary within it from a location accessible in the `PATH`:

    brew cask install basictex
    ln -s /usr/local/texlive/*/bin/x86_64-darwin/xelatex /usr/local/bin/xelatex

[make]: https://www.gnu.org/software/make/
[python]: https://www.python.org
[venv]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
[fontforge]: https://fontforge.org
[fea]: https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html
[xetex]: http://xetex.sourceforge.net
[mupdf]: https://mupdf.com
[repology-xetex]: https://repology.org/project/texlive:xetex/versions
[repology-mupdf]: https://repology.org/project/mupdf/versions
[ubuntu-mupdf]: https://packages.ubuntu.com/eoan/mupdf-tools
[linuxbrew]: https://docs.brew.sh/Homebrew-on-Linux
[homebrew]: https://brew.sh
[basictex]: https://formulae.brew.sh/cask/basictex
