NAME=LinLibertine
VERSION=5.3.1

DIST=$(NAME)-$(VERSION)

SRC=sources
TOOLS=tools

PY=python
BUILD=$(TOOLS)/build.py

FONTS=MR

SFD=$(FONTS:%=$(SRC)/$(NAME)_%.sfd)
OTF=$(FONTS:%=$(NAME)_%.otf)

all: otf

otf: $(OTF)

%.otf: $(SRC)/%.sfd Makefile $(BUILD) $(SRC)/it.sfd $(SRC)/bf.sfd $(SRC)/bi.sfd $(SRC)/sfup.sfd $(SRC)/sfit.sfd $(SRC)/sfbf.sfd
	@echo "Building $@"
	@$(PY) $(BUILD) $< $@ $(VERSION)
