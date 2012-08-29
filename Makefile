NAME=LinLibertine
VERSION=5.3.1

DIST=$(NAME)-$(VERSION)

FF=fontforge -lang=ff
FFLAGES=-1
SCRIPT='Open($$1);\
       if ($$argc>3)\
         MergeFeature($$2);\
       endif;\
       SetFontNames("","","","","","$(VERSION)");\
       Generate($$argv[$$argc-1], "", $(FFLAGES))'

FONTS=MR

SFD=$(FONTS:%=$(NAME)_%.sfd)
OTF=$(FONTS:%=$(NAME)_%.otf)

all: otf

otf: $(OTF)

%.otf: %.sfd Makefile
	@echo "Building $@"
	@$(FF) -c $(SCRIPT) $< $@ 2>/dev/stdout 1>/dev/stderr | tail -n +4
