#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Setup script for Integrated Semantic Framework.
Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

########################################################################

import io
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from coolisf import __author__, __email__
from coolisf import __version__, __license__
from coolisf import __url__, __description__
# from coolisf import __credits__, __maintainer__
# from coolisf import __copyright__, __status__

########################################################################


here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read('README.md', 'CHANGES.md')

setup(
    name='coolisf',
    version=__version__,
    url=__url__,
    license=__license__,
    author=__author__,
    tests_require=[],
    install_requires=[],
    author_email=__email__,
    description=__description__,
    long_description=long_description,
    packages=['coolisf',
              'coolisf/dao',
              'coolisf/mappings',
              'coolisf/parsers',
              'coolisf/processors'],
    include_package_data=True,
    platforms='any',
    test_suite='test',
    classifiers=['Programming Language :: Python',
                 'Development Status :: 0.1 - Alpha',
                 'Natural Language :: English',
                 'Environment :: Console Application',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)
