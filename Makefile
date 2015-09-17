NAME=libertine
VERSION=6.0.0

DIST=$(NAME)-$(VERSION)

SRC=sources
WEB=webfonts
DOC=documentation
TOOLS=tools

PY=python2.7
BUILD=$(TOOLS)/build.py
FINDMISSING=$(TOOLS)/find-missing-glyphs.py
SFNTTOOL=sfnttool
WOFF2_COMPRESS=woff2_compress
SAMPLE=fntsample
OUTLINE=pdfoutline

NULL=

FONTS=math-regular \
      sans-regular sans-bold sans-italic serif-regular \
      serif-semibold serif-bold serif-italic serif-semibolditalic serif-bolditalic \
      serifdisplay-regular \
      serifinitials-regular \
      mono-regular \
      keyboard-regular \
      $(NULL)

SFD=$(FONTS:%=$(SRC)/$(NAME)%.sfd)
OTF=$(FONTS:%=$(NAME)%.otf)
WOFF=$(FONTS:%=$(WEB)/$(NAME)%.woff)
WOF2=$(FONTS:%=$(WEB)/$(NAME)%.woff2)
PDF=$(FONTS:%=$(DOC)/$(NAME)%-table.pdf)

all: otf web

otf: $(OTF)
web: $(WOFF) $(WOF2)
doc: $(PDF)

libertinemath-regular.otf: $(SRC)/libertinemath-regular.sfd $(SRC)/copyright.txt $(SRC)/features/ssty.fea
	@echo "Building $@"
	@$(PY) $(BUILD) -o $@ -v $(VERSION) -i $< -c $(SRC)/copyright.txt -f $(SRC)/features/ssty.fea

%.otf: $(SRC)/%.sfd $(SRC)/copyright.txt
	@echo "Building $@"
	@$(PY) $(BUILD) -o $@ -v $(VERSION) -i $< -c $(SRC)/copyright.txt

$(WEB)/%.woff: %.otf
	@echo "Building $@"
	@mkdir -p $(WEB)
	@$(SFNTTOOL) -w $< $@

$(WEB)/%.woff2: %.otf
	@echo "Building $@"
	@mkdir -p $(WEB)
	@$(WOFF2_COMPRESS) $< 1>/dev/null
	@mv $(@F) $(WEB)

$(DOC)/%-table.pdf: %.otf
	@echo "Generating $@"
	@mkdir -p $(DOC)
	@$(SAMPLE) --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@$(OUTLINE) $@.tmp $@.txt $@
	@rm -f $@.tmp $@.txt

check: $(SFD)
	@$(foreach sfd, $(SFD), \
	     echo "   CHK	"`basename $(sfd)`; \
	     $(PY) $(FINDMISSING) $(sfd); \
	  )
