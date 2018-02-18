#! /bin/bash
for font in $@
do
	if [ -d $font ]; then font=$font/font.props; fi
	sed -e '/\(ModificationTime\|Compacted\|WinInfo\|DisplaySize\|AntiAlias\|FitToEm\):/d' $font > $font.tmp
	md5old=$(md5sum $font)
	md5new=$(md5sum $font.tmp)
	if test "$md5old" = "$md5new"
	then
		rm $font.tmp
	else
		mv $font.tmp $font
	fi
done
