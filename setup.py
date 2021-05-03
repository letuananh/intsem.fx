#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Setup script for Integrated Semantic Framework.
Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

########################################################################

import io
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read('README.md')
pkg_info = {}
exec(read('coolisf/__version__.py'), pkg_info)

setup(
    name='coolisf',
    version=pkg_info["__version__"],
    url=pkg_info["__url__"],
    license=pkg_info["__license__"],
    author=pkg_info["__author__"],
    tests_require=[],
    install_requires=[],
    author_email=pkg_info["__email__"],
    description=pkg_info["__description__"],
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
                 'Development Status :: ' + pkg_info["__status__"],
                 'Natural Language :: English',
                 'Natural Language :: Japanese',
                 'Natural Language :: Indonesian',
                 'Natural Language :: Chinese (Simplified)',
                 'Natural Language :: Chinese (Traditional)',
                 'Environment :: Console Application',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: ' + pkg_info["__license__"],
                 'Operating System :: OS Independent',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)
