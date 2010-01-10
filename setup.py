#!/usr/bin/env python
# -*- coding: utf-8 -*-


from distutils.core import setup
from glob import glob
import os

os.chdir(os.path.abspath(os.path.dirname(__file__)))

#TODO Add license, authors etc 
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
     )
