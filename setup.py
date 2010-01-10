#!/usr/bin/env python
# -*- coding: utf-8 -*-


from distutils.core import setup
from glob import glob
from distutils.command.build import build
from distutils.dep_util import newer
from distutils.log import warn, info, error, fatal
import os
import sys
import subprocess

os.chdir(os.path.abspath(os.path.dirname(__file__)))

PO_DIR = 'po'
MO_DIR = os.path.join('build', 'mo')

DATA_FILES = [("share/cloudsn",
    ["README", "INSTALL", "AUTHORS", "COPYING", "NEWS", "data/cloudsn.desktop"])]

#Icons and UI
DATA_FILES += [("share/cloudsn", glob('data/*.png'))]
DATA_FILES += [("share/cloudsn", glob('data/*.ui'))]

#desktop
DATA_FILES += [('share/applications', ['data/cloudsn.desktop'])]
DATA_FILES += [('share/icons/hicolor/scalable/apps', ['data/cloudsn.svg'])]
DATA_FILES += [('share/pixmaps', ['data/cloudsn.svg'])]
DATA_FILES += [('share/icons/hicolor/24x24/apps', ['data/cloudsn.png'])]

class BuildData(build):
    def run (self):
        build.run (self)

        #if self.distribution.without_gettext:
        #    return

        for po in glob (os.path.join (PO_DIR, '*.po')):
            lang = os.path.basename(po[:-3])
            mo = os.path.join(MO_DIR, lang, 'cloudsn.mo')

            directory = os.path.dirname(mo)
            if not os.path.exists(directory):
                info('creating %s' % directory)
                os.makedirs(directory)

            if newer(po, mo):
                info('compiling %s -> %s' % (po, mo))
                try:
                    rc = subprocess.call(['msgfmt', '-o', mo, po])
                    if rc != 0:
                        raise Warning, "msgfmt returned %d" % rc
                except Exception, e:
                    error("Building gettext files failed.  Try setup.py --without-gettext [build|install]")
                    error("Error: %s" % str(e))
                    sys.exit(1)

        TOP_BUILDDIR='.'
        INTLTOOL_MERGE='intltool-merge'
        #desktop_in='data/terminator.desktop.in'
        #desktop_data='data/terminator.desktop'
        #os.system ("C_ALL=C " + INTLTOOL_MERGE + " -d -u -c " + TOP_BUILDDIR +
        #           "/po/.intltool-merge-cache " + TOP_BUILDDIR + "/po " +
        #           desktop_in + " " + desktop_data)

setup(name='cloudsn',
      version='0.1.1',
      description='Python Distribution Utilities',
      author=r'Jesús Barbero Rodríguez',
      author_email='chuchiperriman@gmail.com',
      url='http://github.com/chuchiperriman',
      package_dir = {'' : 'src'},
      packages=['cloudsn', 'cloudsn.core', 'cloudsn.ui', 'cloudsn.providers'],
      data_files = DATA_FILES,
      scripts=['cloudsn'],
      cmdclass={'build': BuildData},
     )
