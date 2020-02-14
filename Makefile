NAME = Libertinus
VERSION = 6.11

MAKEFLAGS := -s
SHELL = bash

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
COVERAGE = $(addsuffix -coverage.json,$(addprefix $(BUILDDIR)/,$(FONTS)))

# Generate list of final output forms
OTF = $(addsuffix .otf,$(FONTS))
SVG = $(DOCSDIR)/preview.svg
PDF = $(DOCSDIR)/Opentype-Features.pdf $(DOCSDIR)/Sample.pdf $(DOCSDIR)/Math-Sample.pdf

export SOURCE_DATE_EPOCH ?= 0

.SECONDARY:
.ONESHELL:

.PHONY: all otf doc normalize check
all: otf $(SVG)
otf: $(OTF)
doc: $(PDF)
normalize: $(NRM)
check: $(LNT) $(CHK) $(DUP)

nofea=$(strip $(foreach f,Initials Keyboard Mono,$(findstring $f,$1)))

$(BUILDDIR)/%.ff.otf: $(SOURCEDIR)/%.sfd $(GSUB) $(BUILD)
	$(info       BUILD  $(*F))
	mkdir -p $(BUILDDIR)
	$(PY) $(BUILD) \
		--input=$< \
		--output=$@ \
		--version=$(VERSION) \
		--output-feature-file=$(BUILDDIR)/$(*F).fea \
		$(if $(call nofea,$@),,--feature-file=$(GSUB))

$(BUILDDIR)/%.otl.otf: $(BUILDDIR)/%.ff.otf
	$(info         OTL  $(*F))
	fonttools feaLib $(BUILDDIR)/$(*F).fea $< -o $@

$(BUILDDIR)/%.hint.otf: $(BUILDDIR)/%.otl.otf
	$(info        HINT  $(*F))
	rm -rf $@.log
	psautohint $< -o $@ --log $@.log

$(BUILDDIR)/%.subset.otf: $(BUILDDIR)/%.hint.otf
	$(info       PRUNE  $(*F))
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
	$(info   NORMALIZE  $(*F))
	mkdir -p $(BUILDDIR)
	$(PY) $(NORMALIZE) $< $@
	if [ "`diff -u $< $@`" ]; then cp $@ $<; touch $@; fi

$(BUILDDIR)/%.chk: $(SOURCEDIR)/%.sfd $(NORMALIZE)
	$(info   NORMALIZE  $(*F))
	mkdir -p $(BUILDDIR)
	$(PY) $(NORMALIZE) $< $@
	diff -u $< $@ || (rm -rf $@ && false)

$(BUILDDIR)/%.dup: $(SOURCEDIR)/%.sfd $(FINDDUPS)
	$(info       CHECK  $(*F))
	mkdir -p $(BUILDDIR)
	$(PY) $(CHECKERRS) $< $@ || (rm -rf $@ && false)


# Currently ignored errors:
#  2: Self-intersecting glyph
#  5: Missing points at extrema
#  7: More points in a glyph than PostScript allows
# 23: Overlapping hints in a glyph
$(BUILDDIR)/LibertinusKeyboard-Regular.lnt: LibertinusKeyboard-Regular.otf
	$(info        LINT  $(<F))
	mkdir -p $(BUILDDIR)
	fontlint -i2,5,7,23 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

$(BUILDDIR)/LibertinusSerifInitials-Regular.lnt: LibertinusSerifInitials-Regular.otf
	$(info        LINT  $(<F))
	mkdir -p $(BUILDDIR)
	fontlint -i2,5,7,23,34 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

# Currently ignored errors:
#  2: Self-intersecting glyph
#  5: Missing points at extrema
# 34: Bad 'CFF ' table
# 98: Self-intersecting glyph when FontForge is able to correct this
$(BUILDDIR)/%.lnt: %.otf
	$(info        LINT  $(*F))
	mkdir -p $(BUILDDIR)
	fontlint -i2,5,34,98 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

$(DOCSDIR)/preview.svg: $(DOCSDIR)/preview.tex $(OTF)
	$(info         SVG  $@)
	xelatex --interaction=batchmode \
		-output-directory=$(dir $@) \
		$< 1>/dev/null || (cat $(basename $<).log && false)

$(DOCSDIR)/preview.pdf: $(DOCSDIR)/preview.svg
	$(info         PDF  $@)
	mutool draw -q -r 200 -o $< $@

# $(shell echo ttx -t cmap -o - $1.otf)
# $(shell echo pyfontaine --wiki $1.otf)
define unicode_coverage_table =
	$(shell jq -M -e -s -r '.[0:5]' $(BUILDDIR)/$1-coverage.json)
endef

$(DOCSDIR)/Unicode-Coverage.md: $(COVERAGE)
	$(info     MARKDOWN  $@)
	export PS4=; exec > $@ # Redirect all STDOUT to the target file
	cat <<- EOF
		# $(NAME) Unicode Coverage
		$(foreach FONT,$(FONTS),
		## $(subst $(NAME),$(NAME) ,$(subst -, ,$(FONT)))
	
		$(call unicode_coverage_table,$(FONT))
		)
	EOF

# select(.commonName | test("Google|Subset|\\+") | not )  |
# select(.percentCoverage >= 10) |
$(BUILDDIR)/%-coverage.json: %.otf
	pyfontaine --json $< |
	jq -M -e -r \
		'.fonts[0].font.orthographies[].orthography |
			(select(.commonName | test("Unicode Block"))) |
			{
				"orthography": .commonName,
				"percent": .percentCoverage
			}' \
		> $@

.PHONY: dist
dist: check dist-clean $(OTF) $(PDF) $(SVG)
	$(info         DIST  $(DIST).zip)
	install -Dm644 $(OTF) -t $(DIST)
	install -Dm644 {OFL,FONTLOG,AUTHORS}.txt -t $(DIST)
	install -Dm644 README.md -t $(DIST)
	install -Dm644 $(PDF) $(SVG) -t $(DIST)/$(DOCSDIR)
	zip -rq $(DIST).zip $(DIST)

.PHONY: dist-clean
dist-clean:
	rm -rf $(DIST) $(DIST).zip

.PHONY: clean
clean: dist-clean
	rm -rf $(CHK) $(MIS) $(DUP) $(FEA) $(NRM) $(LNT) $(PDF) $(OTF)
