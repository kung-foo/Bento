import os
import subprocess
import re

import setuptools
from distutils.core import setup

VERSION = "0.0.2"
RELEASED = False
if not RELEASED:
    try:
        if os.path.exists(".git"):
            s = subprocess.Popen(["git", "rev-parse", "HEAD"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = s.communicate()[0]
            GIT_VERSION = out.strip()
        else:
            GIT_VERSION = ""
    except WindowsError:
        GIT_VERSION = ""
    FULL_VERSION = VERSION + "dev" + GIT_VERSION
else:
    FULL_VERSION = VERSION

def generate_version_py(filename):
    cnt = """\
# This file was autogenerated
version = '%s'
full_version = '%s'
"""
    cnt = cnt % (VERSION, FULL_VERSION)

    f = open(filename, "w")
    try:
        f.write(cnt)
    finally:
        f.close()
    
DESCR = """\
Toydist is a toy distribution tool for python packages, The goal are
extensibility, flexibility, and easy interoperation with external tools.

Toydist is still in infancy; discussions happen on the NumPy Mailing list
(http://mail.scipy.org/pipermail/numpy-discussion/).
"""

CLASSIFIERS = [
    "Development Status :: 1 - Planning",
    "Intended Audience :: Developers",
    "License :: OSI Approved",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS"
]

METADATA = {
    'name': 'toydist',
    'version': FULL_VERSION,
    'description': 'A toy distribution tool',
    'url': 'http://github.com/cournape/toydist',
    'author': 'David Cournapeau',
    'author_email': 'cournape@gmail.com',
    'license': 'BSD',
    'long_description': DESCR,
    'platforms': 'any',
    'classifiers': CLASSIFIERS,
}

PACKAGE_DATA = {
    'packages': ['toydist', 'toydist.core', 'toydist.commands', 'toydist.private',
                 'toymakerlib'],
    'entry_points': {
        'console_scripts': ['toymaker=toymakerlib.toymaker:noexc_main']
    }
}

if __name__ == '__main__':
    generate_version_py("toydist/__version.py")
    config = {}
    for d in (METADATA, PACKAGE_DATA):
        for k, v in d.items():
            config[k] = v
    setup(**config)
