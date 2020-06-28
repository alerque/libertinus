NAME = Libertinus
VERSION = 6.12

# Tip: this build can run multiple jobs in parallel to greatly reduce build
# time. You can `export MAKEFLAGS="-j$(shell nproc)" or invoke make with an
# argument manually setting the number of jobs to run: `make -j6`
MAKEFLAGS += -s -Otarget
SHELL = bash

DIST = $(NAME)-$(VERSION)

SOURCEDIR = sources
BUILDDIR = build
GSUB = $(SOURCEDIR)/features/gsub.fea
DOCSDIR = documentation
TOOLSDIR = tools

PY ?= python3
BUILD = $(TOOLSDIR)/build.py
NORMALIZE = $(TOOLSDIR)/sfdnormalize.py

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

# Generate list of final output forms
OTF = $(addsuffix .otf,$(FONTS))
SVG = preview.svg
PDF = $(DOCSDIR)/Opentype-Features.pdf $(DOCSDIR)/Sample.pdf $(DOCSDIR)/Math-Sample.pdf

export SOURCE_DATE_EPOCH ?= 0

.SECONDARY:
.ONESHELL:

.PHONY: all otf doc normalize check
all: otf $(SVG)
otf: $(OTF)
doc: $(PDF)
normalize: $(NRM)
check: $(CHK)

nofea=$(strip $(foreach f,Initials Keyboard Mono,$(findstring $f,$1)))

$(BUILDDIR):
	mkdir -p $@

$(BUILDDIR)/%.otl.otf: $(SOURCEDIR)/%.sfd $(GSUB) $(BUILD) | $(BUILDDIR)
	$(info       BUILD  $(*F))
	$(PY) $(BUILD) \
		--input=$< \
		--output=$@ \
		--version=$(VERSION) \
		$(if $(call nofea,$@),,--feature-file=$(GSUB))

$(BUILDDIR)/%.hint.otf: $(BUILDDIR)/%.otl.otf
	$(info        HINT  $(*F))
	rm -rf $@.log
	psautohint $< -o $@ --log $@.log

$(BUILDDIR)/%.subr.otf: $(BUILDDIR)/%.hint.otf
	$(info        SUBR  $(*F))
	$(PY) -m cffsubr -o $@ $<

%.otf: $(BUILDDIR)/%.subr.otf
	cp $< $@

$(BUILDDIR)/%.nrm: $(SOURCEDIR)/%.sfd $(NORMALIZE) | $(BUILDDIR)
	$(info   NORMALIZE  $(*F))
	$(PY) $(NORMALIZE) $< $@
	if [ "`diff -u $< $@`" ]; then cp $@ $<; touch $@; fi

$(BUILDDIR)/%.chk: $(SOURCEDIR)/%.sfd $(NORMALIZE) | $(BUILDDIR)
	$(info   NORMALIZE  $(*F))
	$(PY) $(NORMALIZE) $< $@
	diff -u $< $@ || (rm -rf $@ && false)

preview.svg: $(DOCSDIR)/preview.tex $(OTF) | $(BUILDDIR)
	$(info         SVG  $@)
	xelatex --interaction=batchmode \
		-output-directory=$(BUILDDIR) \
		$< 1> /dev/null || (cat $(BUILDDIR)/$(*F).log && false)

preview.pdf: preview.svg
	$(info         PDF  $@)
	mutool draw -q -r 200 -o $< $@

.PHONY: dist
dist: check dist-clean $(OTF) $(PDF) $(SVG)
	$(info         DIST  $(DIST).zip)
	install -Dm644 -t $(DIST) $(OTF)
	install -Dm644 -t $(DIST) {OFL,FONTLOG,AUTHORS,CONTRIBUTORS}.txt
	install -Dm644 -t $(DIST) {README,CONTRIBUTING}.md
	install -Dm644 -t $(DIST)/$(DOCSDIR) $(PDF) $(SVG)
	zip -rq $(DIST).zip $(DIST)

.PHONY: dist-clean
dist-clean:
	rm -rf $(DIST) $(DIST).zip

.PHONY: clean
clean: dist-clean
	rm -rf $(CHK) $(MIS) $(FEA) $(NRM) $(PDF) $(OTF)
