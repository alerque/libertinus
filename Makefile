NAME = Libertinus
VERSION = 6.11

MAKEFLAGS := -s

DIST = $(NAME)-$(VERSION)

SOURCEDIR = sources
BUILDDIR = build
GSUB = $(SOURCEDIR)/features/gsub.fea
DOCSDIR = documentation
TOOLSDIR = tools

PY ?= python
BUILD = $(TOOLSDIR)/build.py
NORMALIZE = $(TOOLSDIR)/sfdnormalize.py
CHECKERRS = $(TOOLSDIR)/check-errors.py

# Default to explicitly enumerating fonts to build;
# use `make ALLFONTS=true ...` to build all *.sfd files in the source tree or
# use `make FONTS="Face-Style" ...` to make targets for only particular font(s).
ALLFONTS ?= false

# Canonical list of fonts face / and style combinations to build;
# note that order here will be used for some documentation
SERIF_STYLES := Regular Semibold Bold Italic SemiboldItalic BoldItalic
SANS_STYLES  := Regular Bold Italic
REGULAR_ONLY := Math Mono Keyboard SerifDisplay SerifInitials

ifeq ($(ALLFONTS),true)
	FONTS := $(notdir $(basename $(wildcard $(SOURCEDIR)/*.sfd)))
else
	FONTS ?= $(foreach STYLE,$(SERIF_STYLES),$(NAME)Serif-$(STYLE)) \
			 $(foreach STYLE,$(SANS_STYLES),$(NAME)Sans-$(STYLE)) \
			 $(foreach FACE,$(REGULAR_ONLY),$(NAME)$(FACE)-Regular)
endif

# Generate lists of various intermediate forms
SFD = $(addsuffix .sfd,$(addprefix $(SOURCEDIR)/,$(FONTS)))
NRM = $(addsuffix .nrm,$(addprefix $(BUILDDIR)/,$(FONTS)))
CHK = $(addsuffix .chk,$(addprefix $(BUILDDIR)/,$(FONTS)))
DUP = $(addsuffix .dup,$(addprefix $(BUILDDIR)/,$(FONTS)))
LNT = $(addsuffix .lnt,$(addprefix $(BUILDDIR)/,$(FONTS)))

# Generate list of final output forms
OTF = $(addsuffix .otf,$(FONTS))
SVG = $(DOCSDIR)/preview.svg
PDF = $(DOCSDIR)/Opentype-Features.pdf $(DOCSDIR)/Sample.pdf $(DOCSDIR)/Math-Sample.pdf

export SOURCE_DATE_EPOCH ?= 0

.SECONDARY:

all: otf $(SVG)

otf: $(OTF)
doc: $(PDF)
normalize: $(NRM)
check: $(LNT) $(CHK) $(DUP)


nofea=$(strip $(foreach f,Initials Keyboard Mono,$(findstring $f,$1)))

$(BUILDDIR)/%.ff.otf: $(SOURCEDIR)/%.sfd $(GSUB) $(BUILD)
	echo "      BUILD  $(*F)"
	mkdir -p $(BUILDDIR)
	$(PY) $(BUILD) \
		--input=$< \
		--output=$@ \
		--version=$(VERSION) \
		--output-feature-file=$(BUILDDIR)/$(*F).fea \
		$(if $(call nofea,$@),,--feature-file=$(GSUB))

$(BUILDDIR)/%.otl.otf: $(BUILDDIR)/%.ff.otf
	echo "        OTL  $(*F)"
	fonttools feaLib $(BUILDDIR)/$(*F).fea $< -o $@

$(BUILDDIR)/%.hint.otf: $(BUILDDIR)/%.otl.otf
	echo "       HINT  $(*F)"
	rm -rf $@.log
	psautohint $< -o $@ --log $@.log

$(BUILDDIR)/%.subset.otf: $(BUILDDIR)/%.hint.otf
	echo "      PRUNE  $(*F)"
	fonttools subset \
		--unicodes='*' \
		--layout-features='*' \
		--name-IDs='*' \
		--notdef-outline \
		--recalc-average-width \
		--recalc-bounds \
		--drop-tables=FFTM \
		--output-file=$@ \
		$<

%.otf: $(BUILDDIR)/%.subset.otf
	cp $< $@

$(BUILDDIR)/%.nrm: $(SOURCEDIR)/%.sfd $(NORMALIZE)
	echo "  NORMALIZE  $(*F)"
	mkdir -p $(BUILDDIR)
	$(PY) $(NORMALIZE) $< $@
	if [ "`diff -u $< $@`" ]; then cp $@ $<; touch $@; fi

$(BUILDDIR)/%.chk: $(SOURCEDIR)/%.sfd $(NORMALIZE)
	echo "  NORMALIZE  $(*F)"
	mkdir -p $(BUILDDIR)
	$(PY) $(NORMALIZE) $< $@
	diff -u $< $@ || (rm -rf $@ && false)

$(BUILDDIR)/%.dup: $(SOURCEDIR)/%.sfd $(FINDDUPS)
	echo "      CHECK  $(*F)"
	mkdir -p $(BUILDDIR)
	$(PY) $(CHECKERRS) $< $@ || (rm -rf $@ && false)


# Currently ignored errors:
#  2: Self-intersecting glyph
#  5: Missing points at extrema
#  7: More points in a glyph than PostScript allows
# 23: Overlapping hints in a glyph
$(BUILDDIR)/LibertinusKeyboard-Regular.lnt: LibertinusKeyboard-Regular.otf
	echo "       LINT  LibertinusKeyboard-Regular"
	mkdir -p $(BUILDDIR)
	fontlint -i2,5,7,23 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

$(BUILDDIR)/LibertinusSerifInitials-Regular.lnt: LibertinusSerifInitials-Regular.otf
	echo "       LINT  LibertinusSerifInitials-Regular"
	mkdir -p $(BUILDDIR)
	fontlint -i2,5,7,23,34 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

# Currently ignored errors:
#  2: Self-intersecting glyph
#  5: Missing points at extrema
# 34: Bad 'CFF ' table
# 98: Self-intersecting glyph when FontForge is able to correct this
$(BUILDDIR)/%.lnt: %.otf
	echo "       LINT  $(*F)"
	mkdir -p $(BUILDDIR)
	fontlint -i2,5,34,98 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

$(DOCSDIR)/preview.svg: $(DOCSDIR)/preview.tex $(OTF)
	echo "        SVG  $@"
	xelatex --interaction=batchmode \
		-output-directory=$(dir $@) \
		$< 1>/dev/null || (cat $(basename $<).log && false)
	mutool draw -q -r 200 -o $@ $(basename $@).pdf

dist: check $(OTF) $(PDF) $(SVG)
	echo "       DIST  $(DIST).zip"
	rm -rf $(DIST) $(DIST).zip
	mkdir -p $(DIST)/$(DOCSDIR)
	cp $(OTF) $(DIST)
	cp $(PDF) $(SVG) $(DIST)/$(DOCSDIR)
	cp OFL.txt FONTLOG.txt AUTHORS.txt $(DIST)
	cp README.md $(DIST)/README.txt
	zip -rq $(DIST).zip $(DIST)

clean:
	rm -rf $(DIST) $(DIST).zip $(CHK) $(MIS) $(DUP) $(FEA) $(NRM) $(LNT) \
		$(PDF) $(OTF)
