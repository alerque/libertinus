NAME = Libertinus
VERSION = 6.11

MAKEFLAGS := -s -j$(shell nproc) -Otarget
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

$(BUILDDIR)/%.otl.otf: $(SOURCEDIR)/%.sfd $(GSUB) $(BUILD)
	$(info       BUILD  $(*F))
	mkdir -p $(BUILDDIR)
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
	tx -cff +S +b $< $(@D)/$(*F).cff 2> /dev/null
	sfntedit -a CFF=$(@D)/$(*F).cff $< $@

%.otf: $(BUILDDIR)/%.subr.otf
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

preview.svg: $(DOCSDIR)/preview.tex $(OTF)
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
	install -Dm644 $(OTF) -t $(DIST)
	install -Dm644 {OFL,FONTLOG,AUTHORS,CONTRIBUTORS}.txt -t $(DIST)
	install -Dm644 {README,CONTRIBUTING}.md -t $(DIST)
	install -Dm644 $(PDF) $(SVG) -t $(DIST)/$(DOCSDIR)
	zip -rq $(DIST).zip $(DIST)

.PHONY: dist-clean
dist-clean:
	rm -rf $(DIST) $(DIST).zip

.PHONY: clean
clean: dist-clean
	rm -rf $(CHK) $(MIS) $(FEA) $(NRM) $(PDF) $(OTF)
