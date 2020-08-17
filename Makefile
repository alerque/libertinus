PROJECT = Libertinus

STATICOTF = true
STATICTTF =
STATICWOFF =
STATICWOFF2 =
VARIABLETTF =
VARIABLEOTF =
VARIABLEWOFF =
VARIABLEWOFF2 =

GSUB = sources/features/gsub.fea
DOCSDIR = documentation
TOOLSDIR = tools

BUILD = $(TOOLSDIR)/build.py

SERIF_STYLES := Regular Semibold Bold Italic SemiboldItalic BoldItalic
SANS_STYLES  := Regular Bold Italic
REGULAR_ONLY := Math Mono Keyboard SerifDisplay SerifInitials

sfdFamilyNames = $(shell sed -n '/FamilyName/{s/.*: //;s/ //g;p}' $1)

FontStyles = $(SERIF_STYLES)
INSTANCES = $(foreach STYLE,$(SERIF_STYLES),$(PROJECT)Serif-$(STYLE)) \
			$(foreach STYLE,$(SANS_STYLES),$(PROJECT)Sans-$(STYLE)) \
			$(foreach FACE,$(REGULAR_ONLY),$(PROJECT)$(FACE)-Regular)

default: all

nofea=$(strip $(foreach f,Initials Keyboard Mono,$(findstring $f,$1)))

define otf_instance_template =

$$(BUILDDIR)/$1-%-static.otf: sources/$1-%.sfd $(GSUB) $(BUILD) | $$(BUILDDIR)
	$$(PYTHON) $(BUILD) \
		--input=$$< \
		--output=$$@ \
		--version=$$(FontVersion) \
		$$(if $$(call nofea,$$@),,--feature-file=$(GSUB))

$$(BUILDDIR)/$1-%-instance.otf: $$(BUILDDIR)/$1-%-static.otf
	$$(PYTHON) -m cffsubr -o $$@ $$<

endef

$(DOCSDIR)/preview.pdf: $(DOCSDIR)/preview.tex $(STATICOTFS) | $(BUILDDIR)
	xelatex --interaction=batchmode -output-directory=$(BUILDDIR) $<
	cp $(BUILDDIR)/$(@F) $@

preview.svg: $(DOCSDIR)/preview.pdf
	set -x
	mutool draw -q -r 200 -F svg $< 1 > $@

install-dist: install-dist-$(PROJECT)

install-dist-$(PROJECT): | preview.svg
	install -Dm644 -t "$(DISTDIR)/" preview.svg AUTHORS.txt CONTRIBUTING.md CONTRIBUTORS.txt FONTLOG.txt
	install -Dm644 -t "$(DISTDIR)/$(DOCSDIR)" $(DOCSDIR)/*.pdf
