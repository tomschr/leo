#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#

from setuptools import setup


def requires(filename):
    """Returns a list of all pip requirements

    :param filename: the Pip requirement file (usually 'requirements.txt')
    :return: list of modules
    :rtype: list
    """
    modules = []
    with open(filename, 'r') as pipreq:
        for line in pipreq:
            line = line.strip()
            # Checks if line starts with a comment or referencing
            # external pip requirements file (with '-e'):
            if line.startswith('#') or line.startswith('-') or not line:
                continue
            modules.append(line)
    return modules


setup(
    name='leo',
    version='1.1.0',
    license='GPL3',
    description='Translate with leo.org',
    author='Thomas Schraitle',
    author_email='toms@opensuse.org',
    url='https://github.com/tomschr/leo',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
        'Topic :: Text Processing',
        ],
    #
    install_requires=requires('requirements.txt'),
    # Testing:
    setup_requires=['pytest-runner', ],
    tests_require=requires('devel_requirements.txt'),
    #
    scripts=['bin/leo.py'],
)
