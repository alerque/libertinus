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
      keyboard-regular \
      $(NULL)

SFD=$(FONTS:%=$(SRC)/$(NAME)%.sfd)
OTF=$(FONTS:%=$(NAME)%.otf)

all: otf

otf: $(OTF)

%.otf: $(SRC)/%.sfd
	@echo "Building $@"
	@$(PY) $(BUILD) $@ $(VERSION) $^
