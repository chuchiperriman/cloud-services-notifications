###################################
### Initialization
###################################
AC_INIT([cloudsn], [0.1.0])
AC_CONFIG_SRCDIR(cloudsn)
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE


###################################
### Python modules
###################################
AM_PATH_PYTHON
PKG_CHECK_MODULES(PYGTK, pygtk-2.0)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)


###################################
### GConf
###################################
PKG_CHECK_MODULES(gconf, gconf-2.0)
AM_GCONF_SOURCE_2
AC_PATH_PROG([GCONFTOOL], [gconftool-2], [no])
if test "$GCONFTOOL" = "no"; then
	AC_MSG_ERROR([gconftool-2 not found])
fi


###################################
### Internationalization
###################################
GETTEXT_PACKAGE=cloudsn
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])


###################################
### Config and output
###################################
AC_CONFIG_FILES([
	Makefile
	data/Makefile
	data/cloudsn.desktop.in.in
	po/Makefile.in
	cloudsn/Makefile
	cloudsn/core/Makefile
	cloudsn/ui/Makefile
	cloudsn/providers/Makefile
])
AC_OUTPUT
