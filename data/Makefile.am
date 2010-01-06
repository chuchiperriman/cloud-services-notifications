# ******************************************************************************
# GConf Schemas
# ******************************************************************************
# GConf Preference Schemas
#schemadir = $(GCONF_SCHEMA_FILE_DIR)
#schema_in_files = deskbar-applet.schemas.in
#schema_DATA = $(schema_in_files:.schemas.in=.schemas)

# ******************************************************************************
# Misc data
# ******************************************************************************
resourcesdir = $(pkgdatadir)
resources_DATA = \
	preferences.ui		\
	cloudsn.png		\
	gmail-account.ui	\
	gmail.png		\
	greader-account.ui	\
	greader.png		\
	pop3-account.ui		\
	pop3.png

cloudsnbindir = $(libexecdir)/cloudsn

###################################
### Desktop file
###################################
@INTLTOOL_DESKTOP_RULE@
desktop_in_files = cloudsn.desktop.in.in
desktopdir = $(datadir)/applications
desktop_DATA = $(desktop_in_files:.desktop.in.in=.desktop)

cloudsn.desktop.in: cloudsn.desktop.in.in
	sed \
	-e s!\@RESOURCEDIR\@!$(datadir)/$(PACKAGE_NAME)! \
	-e s!\@BINDIR\@!$(bindir)! \
	< $< > $@

DISTCLEANFILES = $(desktop_DATA) cloudsn.desktop.in

EXTRA_DIST = \
	$(resources_DATA) \
	cloudsn.desktop.in.in.in
	
	
