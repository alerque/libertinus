NAME=libertinus
VERSION=6.6

DIST=$(NAME)-$(VERSION)

SRC=sources
FEA=$(SRC)/features
DOC=documentation
TOOLS=tools

PY=python
BUILD=$(TOOLS)/build.py
NORMALIZE=$(TOOLS)/sfdnormalize.py
CHECKERRS=$(TOOLS)/check-errors.py

NULL=

FONTS=math-regular \
      sans-regular \
      sans-bold \
      sans-italic \
      serif-regular \
      serif-semibold \
      serif-bold \
      serif-italic \
      serif-semibolditalic \
      serif-bolditalic \
      serifdisplay-regular \
      serifinitials-regular \
      mono-regular \
      keyboard-regular \
      $(NULL)

SFD=$(FONTS:%=$(SRC)/$(NAME)%.sfd)
NRM=$(FONTS:%=$(SRC)/$(NAME)%.nrm)
CHK=$(FONTS:%=$(SRC)/$(NAME)%.chk)
DUP=$(FONTS:%=$(SRC)/$(NAME)%.dup)
OTF=$(FONTS:%=$(NAME)%.otf)
PDF=$(FONTS:%=$(DOC)/$(NAME)%-table.pdf)

all: otf

otf: $(OTF)
doc: $(PDF)
normalize: $(NRM)
check: $(CHK) $(DUP)


%.fea:
	@if test ! -f $@; then touch $@; fi

%.otf: $(SRC)/%.sfd $(FEA)/%.fea $(BUILD)
	@echo "   OTF	$@"
	@$(PY) $(BUILD) -o $@ -v $(VERSION) -i $< -f $(FEA)/$(@:%.otf=%.fea)

%.nrm: %.sfd $(NORMALIZE)
	@echo "   NRM	$(<F)"
	@$(PY) $(NORMALIZE) $< $@
	@if [ "`diff -u $< $@`" ]; then cp $@ $<; touch $@; fi

%.chk: %.sfd $(NORMALIZE)
	@echo "   NRM	$(<F)"
	@$(PY) $(NORMALIZE) $< $@
	@diff -u $< $@ || (rm -rf $@ && false)

%.dup: %.sfd $(FINDDUPS)
	@echo "   CHK	$(<F)"
	@$(PY) $(CHECKERRS) $< $@ || (rm -rf $@ && false)

$(DOC)/%-table.pdf: %.otf
	@echo "   PDF	$@"
	@mkdir -p $(DOC)
	@fntsample --font-file $< --output-file $@.tmp                         \
		   --write-outline --use-pango                                 \
		   --style="header-font: Noto Sans Bold 12"                    \
		   --style="font-name-font: Noto Serif Bold 12"                \
		   --style="table-numbers-font: Noto Sans 10"                  \
		   --style="cell-numbers-font:Noto Sans Mono 8"
	@if mutool info $@.tmp &> /dev/null; then                              \
	   mutool clean -d -i -f -a $@.tmp $@;                                 \
	 else                                                                  \
	   cp $@.tmp $@;                                                       \
	 fi
	@rm -f $@.tmp

dist: check $(OTF) $(PDF)
	@echo "   DST	$(DIST).zip"
	@rm -rf $(DIST) $(DIST).zip
	@mkdir -p $(DIST)/$(DOC)
	@cp $(OTF) $(DIST)
	@cp $(PDF) $(DIST)/$(DOC)
	@cp $(DOC)/$(NAME)-testmath.pdf $(DIST)/$(DOC)
	@cp $(DOC)/$(NAME)-sample.pdf $(DIST)/$(DOC)
	@cp OFL.txt FONTLOG.txt AUTHORS.txt $(DIST)
	@cp README.md $(DIST)/README.txt
	@zip -rq $(DIST).zip $(DIST)

clean:
	@rm -rf $(DIST) $(DIST).zip $(CHK) $(MIS) $(DUP) $(NRM) $(OTF) $(PDF)
