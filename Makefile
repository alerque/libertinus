NAME=libertinus
VERSION=6.5

DIST=$(NAME)-$(VERSION)

SRC=sources
FEA=$(SRC)/features
DOC=documentation
TOOLS=tools

PY=python
BUILD=$(TOOLS)/build.py
NORMALIZE=$(TOOLS)/sfdnormalize.py
FINDMISSING=$(TOOLS)/find-missing-glyphs.py
FINDDUPS=$(TOOLS)/find-duplicate-glyphs.py

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
MIS=$(FONTS:%=$(SRC)/$(NAME)%.mis)
DUP=$(FONTS:%=$(SRC)/$(NAME)%.dup)
OTF=$(FONTS:%=$(NAME)%.otf)
PDF=$(FONTS:%=$(DOC)/$(NAME)%-table.pdf)

all: otf

otf: $(OTF)
doc: $(PDF)
normalize: $(NRM)
check: $(CHK) $(MIS) $(DUP)


%.fea:
	@if test ! -f $@; then touch $@; fi

%.otf: $(SRC)/%.sfd $(FEA)/%.fea $(BUILD)
	@echo "   OTF	$@"
	@$(PY) $(BUILD) -o $@ -v $(VERSION) -i $< -f $(FEA)/$(@:%.otf=%.fea)

%.nrm: %.sfd
	@echo "   NRM	$(<F)"
	@$(PY) $(NORMALIZE) $< $@
	@if [ "`diff -u $< $@`" ]; then cp $@ $<; fi

%.chk: %.sfd
	@echo "   CHK	$(<F)"
	@$(PY) $(NORMALIZE) $< $@
	@diff -u $< $@
	@rm -rf $@

%.mis: %.sfd
	@echo "   MIS	$(<F)"
	@$(PY) $(FINDMISSING) $<

%.dup: %.sfd
	@echo "   DUP	$(<F)"
	@$(PY) $(FINDDUPS) $<

$(DOC)/%-table.pdf: %.otf
	@echo "Generating $@"
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
	@echo "Making dist tarball"
	@mkdir -p $(DIST)/$(DOC)
	@cp $(OTF) $(DIST)
	@cp $(PDF) $(DIST)/$(DOC)
	@cp $(DOC)/$(NAME)-testmath.pdf $(DIST)/$(DOC)
	@cp $(DOC)/$(NAME)-sample.pdf $(DIST)/$(DOC)
	@cp OFL.txt FONTLOG.txt AUTHORS.txt $(DIST)
	@cp README.md $(DIST)/README.txt
	@zip -r $(DIST).zip $(DIST)

clean:
	@rm -rf $(DIST) $(DIST).zip
