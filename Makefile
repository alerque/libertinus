NAME=LinLibertine
VERSION=5.3.1

DIST=$(NAME)-$(VERSION)

TOOLS=tools

PY=python
BUILD=$(TOOLS)/build.py

FONTS=MR

SFD=$(FONTS:%=$(NAME)_%.sfd)
OTF=$(FONTS:%=$(NAME)_%.otf)

all: otf

otf: $(OTF)

%.otf: %.sfd Makefile $(BUILD) it.sfd bf.sfd bi.sfd sfup.sfd sfit.sfd sfbf.sfd
	@echo "Building $@"
	@$(PY) $(BUILD) $< $@ $(VERSION)
