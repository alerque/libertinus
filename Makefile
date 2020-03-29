NAME=Libertinus
VERSION=6.11

DIST=$(NAME)-$(VERSION)

SOURCEDIR=sources
BUILDDIR=build
GSUB=$(SOURCEDIR)/features/gsub.fea
DOC=documentation
TOOLS=tools

PY?=python3
BUILD=$(TOOLS)/build.py
NORMALIZE=$(TOOLS)/sfdnormalize.py

NULL=

FONTS=Sans-Regular \
       Sans-Bold \
       Sans-Italic \
       Serif-Regular \
       Serif-Semibold \
       Serif-Bold \
       Serif-Italic \
       Serif-SemiboldItalic \
       Serif-BoldItalic \
       SerifDisplay-Regular \
       Math-Regular \
       SerifInitials-Regular \
       Mono-Regular \
       Keyboard-Regular \
       $(NULL)

SFD=$(FONTS:%=$(SOURCEDIR)/$(NAME)%.sfd)
NRM=$(FONTS:%=$(BUILDDIR)/$(NAME)%.nrm)
CHK=$(FONTS:%=$(BUILDDIR)/$(NAME)%.chk)
OTF=$(FONTS:%=$(NAME)%.otf)
SVG=$(DOC)/preview.svg
PDF=$(DOC)/Opentype-Features.pdf $(DOC)/Sample.pdf $(DOC)/Math-Sample.pdf

export SOURCE_DATE_EPOCH ?= 0

.SECONDARY:

all: otf $(SVG)

otf: $(OTF)
doc: $(PDF)
normalize: $(NRM)
check: $(CHK)


nofea=$(strip $(foreach f,Initials Keyboard Mono,$(findstring $f,$1)))

$(BUILDDIR)/%.otl.otf: $(SOURCEDIR)/%.sfd $(GSUB) $(BUILD)
	@echo "      BUILD  $(*F)"
	@mkdir -p $(BUILDDIR)
	@$(PY) $(BUILD)                                                        \
		--input=$<                                                     \
		--output=$@                                                    \
		--version=$(VERSION)                                           \
		$(if $(call nofea,$@),,--feature-file=$(GSUB))                 \
		;

$(BUILDDIR)/%.hint.otf: $(BUILDDIR)/%.otl.otf
	@echo "       HINT  $(*F)"
	@rm -rf $@.log
	@psautohint $< -o $@ --log $@.log

$(BUILDDIR)/%.subr.otf: $(BUILDDIR)/%.hint.otf
	@echo "       SUBR  $(*F)"
	@tx -cff +S +b $< $(@D)/$(*F).cff 2>/dev/null
	@sfntedit -a CFF=$(@D)/$(*F).cff $< $@

%.otf: $(BUILDDIR)/%.subr.otf
	@cp $< $@

$(BUILDDIR)/%.nrm: $(SOURCEDIR)/%.sfd $(NORMALIZE)
	@echo "  NORMALIZE  $(*F)"
	@mkdir -p $(BUILDDIR)
	@$(PY) $(NORMALIZE) $< $@
	@if [ "`diff -u $< $@`" ]; then cp $@ $<; touch $@; fi

$(BUILDDIR)/%.chk: $(SOURCEDIR)/%.sfd $(NORMALIZE)
	@echo "  NORMALIZE  $(*F)"
	@mkdir -p $(BUILDDIR)
	@$(PY) $(NORMALIZE) $< $@
	@diff -u $< $@ || (rm -rf $@ && false)

$(DOC)/%.svg: $(DOC)/%.tex $(OTF)
	@echo "        SVG  $(*F)"
	@xelatex --interaction=batchmode -output-directory=$(BUILDDIR) $< 1>/dev/null || (cat $(BUILDDIR)/$(*F).log && false)
	@mutool draw -q -r 200 -o $@ $(BUILDDIR)/$(*F).pdf

dist: check $(OTF) $(PDF) $(SVG)
	@echo "       DIST  $(DIST).zip"
	@rm -rf $(DIST) $(DIST).zip
	@mkdir -p $(DIST)/$(DOC)
	@cp $(OTF) $(DIST)
	@cp $(PDF) $(SVG) $(DIST)/$(DOC)
	@cp OFL.txt FONTLOG.txt AUTHORS.txt CONTRIBUTORS.txt $(DIST)
	@cp README.md $(DIST)/README.txt
	@cp CONTRIBUTING.md $(DIST)/CONTRIBUTING.txt
	@zip -rq $(DIST).zip $(DIST)

clean:
	@rm -rf $(DIST) $(DIST).zip $(CHK) $(MIS) $(FEA) $(NRM) $(PDF) $(OTF)
