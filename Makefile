NAME=libertine
VERSION=5.3.0

DIST=$(NAME)-$(VERSION)

SRC=sources
TOOLS=tools

PY=python
BUILD=$(TOOLS)/build.py

NULL=

FONTS=math-regular \
      sans-regular sans-bold sans-italic serif-regular \
      serif-semibold serif-bold serif-italic serif-semibolditalic serif-bolditalic \
      serifdisplay-regular \
      serifinitials-regular \
      mono-regular \
      $(NULL)

SFD=$(FONTS:%=$(SRC)/$(NAME)%.sfd)
OTF=$(FONTS:%=$(NAME)%.otf)

all: otf

otf: $(OTF)

libertinemath-regular.otf: $(SRC)/libertinemath-regular.sfd $(SRC)/it.sfd $(SRC)/bf.sfd $(SRC)/bi.sfd $(SRC)/sfup.sfd $(SRC)/sfit.sfd $(SRC)/sfbf.sfd
	@echo "Building $@"
	@$(PY) $(BUILD) $@ $(VERSION) $^

%.otf: $(SRC)/%.sfd
	@echo "Building $@"
	@$(PY) $(BUILD) $@ $(VERSION) $^
