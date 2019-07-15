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


###############################################
## Building the C++ extension
###############################################

extra_compile_args = ['-w', '-std=c++11', '-O3']
extra_link_args = []

if sys.platform.startswith('darwin'):  # OS X, should work in 10.9+
    extra_compile_args += ['-D NO_TR1_MEMORY', '-stdlib=libc++']
    extra_link_args += ['-stdlib=libc++']
    
    if os.environ.get('USEOPENMP'):
        extra_compile_args += ['-fopenmp']

elif sys.platform.startswith('win'):  # Windows
    extra_compile_args = ['/w', '/openmp']

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

version = '0.4.1'

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

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
    ext_modules=[cyaccess],
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
    tests_require=[
        'pycodestyle',
        'pytest'
    ],
    cmdclass={
        'test': PyTest,
        'lint': Lint,
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU Affero General Public License v3'
    ],
)
