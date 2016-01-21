NAME=libertinus
VERSION=6.2

DIST=$(NAME)-$(VERSION)

SRC=sources
DOC=documentation
TOOLS=tools

PY=python2.7
BUILD=$(TOOLS)/build.py
FINDMISSING=$(TOOLS)/find-missing-glyphs.py
SFNTTOOL=sfnttool
SAMPLE=fntsample
OUTLINE=pdfoutline

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
OTF=$(FONTS:%=$(NAME)%.otf)
PDF=$(FONTS:%=$(DOC)/$(NAME)%-table.pdf)

all: otf

otf: $(OTF)
doc: $(PDF)

$(NAME)math-regular.otf: $(SRC)/$(NAME)math-regular.sfd $(SRC)/copyright.txt $(SRC)/features/ssty.fea Makefile $(BUILD)
	@echo "Building $@"
	@$(PY) $(BUILD) -o $@ -v $(VERSION) -i $< -c $(SRC)/copyright.txt -f $(SRC)/features/ssty.fea

%.otf: $(SRC)/%.sfd $(SRC)/copyright.txt Makefile $(BUILD)
	@echo "Building $@"
	@$(PY) $(BUILD) -o $@ -v $(VERSION) -i $< -c $(SRC)/copyright.txt

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

dist: check $(OTF) $(PDF)
	@echo "Making dist tarball"
	@mkdir -p $(DIST)/$(DOC)
	@cp $(OTF) $(DIST)
	@cp $(PDF) $(DIST)/$(DOC)
	@cp $(DOC)/$(NAME)-testmath.pdf $(DIST)/$(DOC)
	@cp OFL.txt FONTLOG.txt $(DIST)
	@cp README.md $(DIST)/README.txt
	@zip -r $(DIST).zip $(DIST)

clean:
	@rm -rf $(DIST) $(DIST).zip
