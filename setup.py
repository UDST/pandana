import os
import platform
import sys
import sysconfig

from ez_setup import use_setuptools
use_setuptools()

from setuptools import find_packages
from distutils.core import setup, Extension
from setuptools.command.test import test as TestCommand
from setuptools.command.build_ext import build_ext


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


class Lint(TestCommand):
    def run(self):
        os.system("cpplint --filter=-build/include_subdir,-legal/copyright,-runtime/references,-runtime/int src/accessibility.* src/graphalg.*")
        os.system("pep8 src/cyaccess.pyx")
        os.system("pep8 pandana")


class CustomBuildExtCommand(build_ext):
    """build_ext command for use when numpy headers are needed."""
    def run(self):
        import numpy as np
        self.include_dirs.append(np.get_include())
        build_ext.run(self)


include_dirs = [
    '.'
]

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

source_files = [
    'src/accessibility.cpp',
    'src/graphalg.cpp',
    "src/cyaccess.pyx",
    'src/contraction_hierarchies/src/libch.cpp'
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
        if mac_ver >= [10, 7]:
            extra_compile_args += ['-D NO_TR1_MEMORY']
            extra_compile_args += ['-stdlib=libc++']

version = '0.4.0'

# read long description from README
with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    packages=packages,
    name='pandana',
    author='UrbanSim Inc.',
    version=version,
    license='AGPL',
    description=('Pandas Network Analysis - '
                 'dataframes of network queries, quickly'),
    long_description=long_description,
    url='https://udst.github.io/pandana/',
    ext_modules=[Extension(
            'pandana.cyaccess',
            source_files,
            language="c++",
            include_dirs=include_dirs,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        )],
    install_requires=[
        'matplotlib>=1.3.1',
        'numpy>=1.8.0',
        'pandas>=0.17.0',
        'requests>=2.0',
        'tables>=3.1.0',
        'osmnet>=0.1.2',
        'cython>=0.25.2',
        'scikit-learn>=0.18.1'
    ],
    tests_require=['pytest'],
    cmdclass={
        'test': PyTest,
        'lint': Lint,
        'build_ext': CustomBuildExtCommand,
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: GNU Affero General Public License v3'
    ],
)
