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
