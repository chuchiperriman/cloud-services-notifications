SUBDIRS = core providers ui

###################################
### Main data
###################################
all-local: globals.py

bin_SCRIPTS = cloudsn

cloudsndir = $(pythondir)/cloudsn

cloudsn_PYTHON =				\
	__init__.py					\
	cloudsn
	
nodist_cloudsn_PYTHON =	\
	globals.py

EXTRA_DIST = 				\
	$(bin_SCRIPTS)			\
	$(cloudsn_PYTHON)		\
	globals.py.in

CLEANFILES = \
	globals.py

###################################
### Configure globals.py
###################################
globals.py: globals.py.in Makefile
	sed \
		-e s!\@LOCALEDIR\@!$(datadir)/locale! \
		-e s!\@RESOURCEDIR\@!$(datadir)/$(PACKAGE_NAME)! \
		-e s!\@PKGDATADIR\@!$(pkgdatadir)! \
		-e s!\@PACKAGE\@!$(PACKAGE_NAME)! \
		-e s!\@VERSION\@!$(PACKAGE_VERSION)! \
		< $< \
		> $@
