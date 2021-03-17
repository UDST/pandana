import os
import platform
import sys
import sysconfig

from setuptools import find_packages, setup, Extension
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
        errno = pytest.main(self.pytest_args or [''])
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

    extra_compile_args += ['-stdlib=libc++']
    extra_link_args += ['-stdlib=libc++']
    
    # The default compiler that ships with Macs doesn't support OpenMP multi-
    # threading. We recommend using the Conda toolchain instead, but will also
    # try to detect if people are using another alternative like Homebrew.

    if 'CC' in os.environ:
        extra_compile_args += ['-fopenmp']
        print('Attempting Pandana compilation with OpenMP multi-threading '
              'support, with user-specified compiler:\n{}'.format(
              os.environ['CC']))

    # Otherwise, if the default clang has been replaced but nothing specified
    # in the 'CC' environment variable, assume they've followed our instructions
    # for using the Conda toolchain.
    
    elif os.popen('which clang').read().strip() != '/usr/bin/clang':
        cc = 'clang'
        cc_catalina = 'clang --sysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk'
        
        extra_compile_args += ['-fopenmp']
        print('Attempting Pandana compilation with OpenMP multi-threading '
              'support, with the following compiler:\n{}'.format(
              os.popen('which clang').read()))

        if '10.15' in os.popen('sw_vers').read():
            os.environ['CC'] = cc_catalina
        elif '11.' in os.popen('sw_vers').read():
            os.environ['CC'] = cc_catalina
        else:
            os.environ['CC'] = cc

    else:
        print('Attempting Pandana compilation without support for '
              'multi-threading. See installation instructions for alternative '
              'options')

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

version = '0.6.1'

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    packages=packages,
    name='pandana',
    author='UrbanSim Inc.',
    version=version,
    license='AGPL',
    description=('Python library for network analysis'),
    long_description=(
        'Pandana is a Python library for network analysis that uses '
        'contraction hierarchies to calculate super-fast travel '
        'accessibility metrics and shortest paths. The numerical '
        'code is in C++.'),
    url='https://udst.github.io/pandana/',
    ext_modules=[cyaccess],
    python_requires = '>=3.5',
    install_requires=[
        'cython >=0.25.2',
        'numpy >=1.8',
        'pandas >=0.17',
        'requests >=2.0',
        'scikit-learn >=0.18',
        'tables >=3.1, <3.6; python_version <"3.6"',
        'tables >=3.1, <3.7; python_version >="3.6"'
    ],
    cmdclass={
        'test': PyTest,
        'lint': Lint,
        'build_ext': CustomBuildExtCommand,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: GNU Affero General Public License v3'
    ],
)
