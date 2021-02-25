STATICTTF =
STATICWOFF =

GSUB = sources/features/gsub.fea
DOCSDIR = documentation
TOOLSDIR = tools

BUILD = $(TOOLSDIR)/build.py

SERIF_STYLES := Regular Semibold Bold Italic SemiboldItalic BoldItalic
SANS_STYLES  := Regular Bold Italic
REGULAR_ONLY := Math Mono Keyboard SerifDisplay SerifInitials

FontStyles = $(SERIF_STYLES)
INSTANCES = $(foreach STYLE,$(SERIF_STYLES),$(PROJECT)Serif-$(STYLE)) \
			$(foreach STYLE,$(SANS_STYLES),$(PROJECT)Sans-$(STYLE)) \
			$(foreach FACE,$(REGULAR_ONLY),$(PROJECT)$(FACE)-Regular)

nofea=$(strip $(foreach f,Initials Keyboard Mono,$(findstring $f,$1)))

define otf_instance_template =

$$(BUILDDIR)/$1-%-instance.otf: $$(BUILDDIR)/$1-%-normalized.sfd $(GSUB) $(BUILD)
	$$(PYTHON) $(BUILD) \
		--input=$$< \
		--output=$$@ \
		$$(if $$(call nofea,$$@),,--feature-file=$(GSUB))

endef

$(DOCSDIR)/preview.pdf: $(DOCSDIR)/preview.tex $(STATICOTFS) | $(BUILDDIR)
	xelatex --interaction=batchmode -output-directory=$(BUILDDIR) $<
	cp $(BUILDDIR)/$(@F) $@

_scour_args = --quiet --set-precision=4 --remove-metadata --enable-id-stripping --strip-xml-prolog --strip-xml-space --no-line-breaks --no-renderer-workaround

preview.svg: $(DOCSDIR)/preview.pdf
	mutool draw -r 200 -F svg $< 1 |
		sed -e '/^<g /a <rect width="100%" height="100%" fill="white" />' > $@

install-dist: install-dist-$(PROJECT)

install-dist-$(PROJECT): | preview.svg
	install -Dm644 -t "$(DISTDIR)/" preview.svg AUTHORS.txt CONTRIBUTING.md CONTRIBUTORS.txt FONTLOG.txt
	install -Dm644 -t "$(DISTDIR)/$(DOCSDIR)" $(DOCSDIR)/*.pdf

CTAN_NAME = libertinus-fonts

.PHONY: dist-ctan
dist-ctan: install-dist
	mktemp ctan-XXXXXX.zip | read TMP
	bsdtar \
		-s ',$(DISTDIR),$(CTAN_NAME),' \
		-s ',static/OTF,otf,' \
		-acf $${TMP} $(DISTDIR)
	bsdtar -acf $(CTAN_NAME)-$(FontVersion).tar.gz --exclude 'static' @$${TMP}
	rm $${TMP}
