NAME=Libertinus
VERSION=6.7

DIST=$(NAME)-$(VERSION)

SRC=sources
FEADIR=$(SRC)/features
GSUB=$(FEADIR)/gsub.fea
DOC=documentation
TOOLS=tools

PY?=python
PREPROP?=preprocess
BUILD=$(TOOLS)/build.py
LOADFEAT=$(TOOLS)/load-features.py
NORMALIZE=$(TOOLS)/sfdnormalize.py
CHECKERRS=$(TOOLS)/check-errors.py
LO?=lowriter

NULL=

MFONTS=Sans-Regular \
       Sans-Bold \
       Sans-Italic \
       Serif-Regular \
       Serif-Semibold \
       Serif-Bold \
       Serif-Italic \
       Serif-SemiboldItalic \
       Serif-BoldItalic \
       SerifDisplay-Regular \
       $(NULL)

OFONTS=Math-Regular \
       SerifInitials-Regular \
       Mono-Regular \
       Keyboard-Regular \
       $(NULL)

FONTS=$(MFONTS) \
      $(OFONTS)

SFD=$(FONTS:%=$(SRC)/$(NAME)%.sfd)
MNRM=$(MFONTS:%=$(SRC)/$(NAME)%.nrm)
ONRM=$(OFONTS:%=$(SRC)/$(NAME)%.nrm)
NRM=$(MNRM) $(ONRM)
FEA=$(MFONTS:%=$(SRC)/$(NAME)%.fea)
MCHK=$(MFONTS:%=$(SRC)/$(NAME)%.chk)
OCHK=$(OFONTS:%=$(SRC)/$(NAME)%.chk)
CHK=$(MCHK) $(OCHK)
DUP=$(FONTS:%=$(SRC)/$(NAME)%.dup)
LNT=$(FONTS:%=$(NAME)%.lnt)
MOTF=$(MFONTS:%=$(NAME)%.otf)
OOTF=$(OFONTS:%=$(NAME)%.otf)
OTF=$(MOTF) $(OOTF)
PDF=$(FONTS:%=$(DOC)/$(NAME)%-Table.pdf)
OPDF=$(DOC)/Opentype-Features.pdf $(DOC)/Sample.pdf

FEADEFS=

export SOURCE_DATE_EPOCH ?= 0

all: otf

otf: $(OTF)
doc: $(PDF) $(OPDF)
feature-files: $(FEA)
normalize: $(NRM)
check: $(LNT) $(CHK) $(DUP)


%.fea: FEADEFS += $(subst Italic,-D ITALIC,$(findstring Italic,$@))
%.fea: FEADEFS += $(subst Sans,-D SANS,$(findstring Sans,$@))
%.fea: FEADEFS += $(subst Display,-D NOSMALLCAPS,$(findstring Display,$@))
%.fea: %.sfd $(GSUB)
	@echo "   FEA	$@"
	@$(PREPROP) -c $(FEADIR)/pp_content_types $(FEADEFS) -I $(FEADIR) -o $@ $(GSUB)

$(MOTF): %.otf: $(SRC)/%.sfd $(SRC)/%.fea $(BUILD)
	@echo "   OTF	$@"
	@$(PY) $(BUILD) -f $(SRC)/$*.fea -o $@ -v $(VERSION) -i $<

$(OOTF): %.otf: $(SRC)/%.sfd $(BUILD)
	@echo "   OTF	$@"
	@$(PY) $(BUILD) -o $@ -v $(VERSION) -i $<

$(MNRM): TMPFILE = $(subst nrm,tmpnrm,$@)
$(MNRM): %.nrm: %.sfd $(NORMALIZE) $(LOADFEAT)
	@echo "   NRM	$(<F)"
	@$(PY) $(LOADFEAT) -e -o $(TMPFILE) $<
	@$(PY) $(NORMALIZE) $(TMPFILE) $@
	@rm -f $(TMPFILE)
	@if [ "`diff -u $< $@`" ]; then cp $@ $<; touch $@; fi

$(ONRM): %.nrm: %.sfd $(NORMALIZE)
	@echo "   NRM	$(<F)"
	@$(PY) $(NORMALIZE) $< $@
	@if [ "`diff -u $< $@`" ]; then cp $@ $<; touch $@; fi

$(MCHK): TMPFILE = $(subst chk,tmpchk,$@)
$(MCHK): %.chk: %.sfd $(NORMALIZE) $(LOADFEAT)
	@echo "   NRM	$(<F)"
	@$(PY) $(LOADFEAT) -e -o $(TMPFILE) $<
	@$(PY) $(NORMALIZE) $(TMPFILE) $@
	@rm -f $(TMPFILE)
	@diff -u $< $@ || (rm -rf $@ && false)

$(OCHK): %.chk: %.sfd $(NORMALIZE)
	@echo "   NRM	$(<F)"
	@$(PY) $(NORMALIZE) $< $@
	@diff -u $< $@ || (rm -rf $@ && false)

%.dup: %.sfd $(FINDDUPS)
	@echo "   CHK	$(<F)"
	@$(PY) $(CHECKERRS) $< $@ || (rm -rf $@ && false)


# Currently ignored errors:
#  2: Self-intersecting glyph
#  7: More points in a glyph than PostScript allows
#  5: Missing points at extrema
# 23: Overlapping hints in a glyph
LibertinusKeyboard-Regular.lnt: LibertinusKeyboard-Regular.otf
	@echo "   LNT  $(<F)"
	@fontlint -i2,5,7,23 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

LibertinusSerifInitials-Regular.lnt: LibertinusSerifInitials-Regular.otf
	@echo "   LNT  $(<F)"
	@fontlint -i2,5,7,23 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

# Currently ignored errors:
#  5: Missing points at extrema
# 34: Bad 'CFF ' table
%.lnt: %.otf
	@echo "   LNT	$(<F)"
	@fontlint -i5,34 $< 2>/dev/null 1>$@ || (cat $@ && rm -rf $@ && false)

$(DOC)/%-Table.pdf: %.otf
	@echo "   PDF	$@"
	@mkdir -p $(DOC)
	@fntsample --font-file $< --output-file $@                             \
		   --write-outline --use-pango                                 \
		   --style="header-font: Noto Sans Bold 12"                    \
		   --style="font-name-font: Noto Serif Bold 12"                \
		   --style="table-numbers-font: Noto Sans 10"                  \
		   --style="cell-numbers-font:Noto Sans Mono 8"

$(DOC)/%.pdf: $(DOC)/%.fodt
	@echo "   PDF	$@"
	@mkdir -p $(DOC)
	@VCL_DEBUG_DISABLE_PDFCOMPRESSION=1 LC_ALL=en_US.utf-8 \
	 $(LO) --convert-to pdf --outdir $(DOC) $< 1> /dev/null

dist: check $(OTF) $(PDF) $(OPDF)
	@echo "   DST	$(DIST).zip"
	@rm -rf $(DIST) $(DIST).zip
	@mkdir -p $(DIST)/$(DOC)
	@cp $(OTF) $(DIST)
	@cp $(PDF) $(OPDF) $(DIST)/$(DOC)
	@cp $(DOC)/Math-Sample.pdf $(DIST)/$(DOC)
	@cp OFL.txt FONTLOG.txt AUTHORS.txt $(DIST)
	@cp README.md $(DIST)/README.txt
	@zip -rq $(DIST).zip $(DIST)

less-clean:
	@rm -rf $(DIST) $(DIST).zip $(CHK) $(MIS) $(DUP) $(FEA) $(NRM) $(LNT)

clean: less-clean
	@rm -rf $(MOTF) $(OOTF) $(PDF) $(OPDF)
