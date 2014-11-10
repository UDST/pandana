import os
import platform
import sys
import sysconfig

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension, find_packages
from setuptools.command.test import test as TestCommand
import numpy as np


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args or '')
        sys.exit(errno)

include_dirs = [
    np.get_include(),
    '.',
    'src/ann_1.1.2/include'
]

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

source_files = [
    'src/accessibility.cpp',
    'src/graphalg.cpp',
    'src/nearestneighbor.cpp',
    'src/pyaccesswrap.cpp',
    'src/contraction_hierarchies/src/libch.cpp',
    'src/ann_1.1.2/src/ANN.cpp',
    'src/ann_1.1.2/src/brute.cpp',
    'src/ann_1.1.2/src/kd_tree.cpp',
    'src/ann_1.1.2/src/kd_util.cpp',
    'src/ann_1.1.2/src/kd_split.cpp',
    'src/ann_1.1.2/src/kd_dump.cpp',
    'src/ann_1.1.2/src/kd_search.cpp',
    'src/ann_1.1.2/src/kd_pr_search.cpp',
    'src/ann_1.1.2/src/kd_fix_rad_search.cpp',
    'src/ann_1.1.2/src/bd_tree.cpp',
    'src/ann_1.1.2/src/bd_search.cpp',
    'src/ann_1.1.2/src/bd_pr_search.cpp',
    'src/ann_1.1.2/src/bd_fix_rad_search.cpp',
    'src/ann_1.1.2/src/perf.cpp'
]

extra_compile_args = [
    '-w',
    '-std=c++0x',
    '-O3',
    '-fpic',
    '-g',
]
extra_link_args = None

# separate compiler options for Windows
if sys.platform.startswith('win'):
    extra_compile_args = ['/w', '/openmp']
# Use OpenMP if directed or not on a Mac
elif os.environ.get('USEOPENMP') or not sys.platform.startswith('darwin'):
    extra_compile_args += ['-fopenmp']
    extra_link_args = [
        '-lgomp'
    ]

# recent versions of the OS X SDK don't have the tr1 namespace
# and we need to flag that during compilation.
# here we need to check what version of OS X is being targeted
# for the installation.
# this is potentially different than the version of OS X on the system.
if platform.system() == 'Darwin':
    mac_ver = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
    if mac_ver:
        mac_ver = [int(x) for x in mac_ver.split('.')]
        if mac_ver >= [10, 9]:
            extra_compile_args += ['-D NO_TR1_MEMORY']

version = '0.1.2'

# read long description from README
with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    packages=packages,
    name='pandana',
    version=version,
    license='AGPL',
    description=('Pandas Network Analysis - '
                 'dataframes of network queries, quickly'),
    long_description=long_description,
    url='http://synthicity.github.io/pandana/',
    ext_modules=[
        Extension(
            'pandana._pyaccess',
            source_files,
            include_dirs=include_dirs,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args
        )
    ],
    install_requires=[
        'brewer2mpl>=1.4',
        'matplotlib>=1.3.1',
        'numpy>=1.8.0',
        'pandas>=0.13.1',
        'tables>=3.1.0'
    ],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU Affero General Public License v3'
    ],
)
