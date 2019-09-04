import os
import platform
import sys
import sysconfig

from setuptools import find_packages
from distutils.core import setup, Extension
from setuptools.command.test import test as TestCommand
from setuptools.command.build_ext import build_ext


###############################################
## Invoking tests
###############################################

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
        os.system("pycodestyle src/cyaccess.pyx")
        os.system("pycodestyle pandana")


class CustomBuildExtCommand(build_ext):
    """build_ext command for use when numpy headers are needed."""
    def run(self):
        import numpy as np
        self.include_dirs.append(np.get_include())
        build_ext.run(self)


###############################################
## Building the C++ extension
###############################################

extra_compile_args = ['-w', '-std=c++11', '-O3']
extra_link_args = []

# Mac compilation: flags are for the llvm compilers included with recent
# versions of Xcode Command Line Tools, or newer versions installed separately

if sys.platform.startswith('darwin'):  # Mac
    
    # This environment variable sets the earliest OS version that the compiled
    # code will be compatible with. In certain contexts the default is too old
    # to allow using libc++; supporting OS X 10.9 and later seems safe
    os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.9'
    
    extra_compile_args += ['-D NO_TR1_MEMORY', '-stdlib=libc++']
    extra_link_args += ['-stdlib=libc++']
    
    # This checks if the user has replaced the default clang compiler (this does
    # not confirm there's OpenMP support, but is the best we could come up with)
    if os.popen('which clang').read() != '/usr/bin/clang':
        os.environ['CC'] = 'clang'
        extra_compile_args += ['-fopenmp']

# Window compilation: flags are for Visual C++

elif sys.platform.startswith('win'):  # Windows
    extra_compile_args = ['/w', '/openmp']

# Linux compilation: flags are for gcc 4.8 and later

else:  # Linux
    extra_compile_args += ['-fopenmp']
    extra_link_args += ['-lgomp']


cyaccess = Extension(
        name='pandana.cyaccess',
        sources=[
            'src/accessibility.cpp',
            'src/graphalg.cpp',
            'src/cyaccess.pyx',
            'src/contraction_hierarchies/src/libch.cpp'],
        language='c++',
        include_dirs=['.'],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args)


###############################################
## Standard setup
###############################################

version = '0.4.4'

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    packages=packages,
    name='pandana',
    author='UrbanSim Inc.',
    version=version,
    license='AGPL',
    description=('Pandas Network Analysis - '
                 'dataframes of network queries, quickly'),
    long_description=(
        'Pandana performs hundreds of thousands of network queries in under a '
        'second (for walking-scale distances) using a Pandas-like API. The '
        'computations are parallelized for multi-core machines using an '
        'underlying C++ library.'),
    url='https://udst.github.io/pandana/',
    ext_modules=[cyaccess],
    install_requires=[
        'cython >=0.25.2',
        'matplotlib >=1.3.1',
        'numpy >=1.8.0',
        'osmnet >=0.1.2',
        'pandas >=0.17.0',
        'requests >=2.0',
        'scikit-learn >=0.18.1',
        'tables >=3.1.0'
    ],
    tests_require=[
        'pycodestyle',
        'pytest'
    ],
    cmdclass={
        'test': PyTest,
        'lint': Lint,
        'build_ext': CustomBuildExtCommand,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU Affero General Public License v3'
    ],
)
