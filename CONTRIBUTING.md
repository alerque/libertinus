Contributing
------------

The source files are under the `sources` subdirectory. The `.sfd` files are
FontForge source font format and should be edited with FontForge. The `.fea`
files are Adobe feature files and should be edited by a plain text editor.

After modifying the SFD files, they must be normalized with:

    make normalize

(Make sure to save a copy of the SFD files before running this tool. The
simplest way is to commit the SFD files, normalize, check the diffs and verify
they are OK, then `git commit --amend` the changes).

We keep the generated fonts under version control, so the last step is to run
`make` and commit the modified sources and the generated fonts.

Fonts must be generated for each commit that changes the source files.
The build tools are smart enuogh to not change teh binary fonts if the sources
were not changed
