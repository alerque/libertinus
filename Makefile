NAME=LinLibertine
VERSION=5.3.1

DIST=$(NAME)-$(VERSION)

PY=python

define $(NAME)SCRIPT
import fontforge, sys
f = fontforge.open(sys.argv[1])
if len(sys.argv) > 3:
  f.mergeFeature(sys.argv[3])
f.mergeFonts("it.sfd")
f.mergeFonts("bf.sfd")
f.mergeFonts("bi.sfd")
f.mergeFonts("sfup.sfd")
f.mergeFonts("sfit.sfd")
f.mergeFonts("sfbf.sfd")
f.version = "$(VERSION)"
f.generate(sys.argv[2], flags=("round", "opentype"))
endef

export $(NAME)SCRIPT

FONTS=MR

SFD=$(FONTS:%=$(NAME)_%.sfd)
OTF=$(FONTS:%=$(NAME)_%.otf)

all: otf

otf: $(OTF)

%.otf: %.sfd Makefile it.sfd bf.sfd bi.sfd sfup.sfd sfit.sfd sfbf.sfd
	@echo "Building $@"
	@$(PY) -c "$$$(NAME)SCRIPT" $< $@
