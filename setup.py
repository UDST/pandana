import os
import sys

import numpy as np  # for c++ headers

from setuptools import find_packages, setup, Extension


###############################################
# Building the C++ extension
###############################################

extra_compile_args = ["-w", "-std=c++17", "-O3"]
extra_link_args = []

# Mac compilation: flags are for the llvm compilers included with recent
# versions of Xcode Command Line Tools, or newer versions installed separately

if sys.platform.startswith("darwin"):  # Mac

    extra_compile_args += ["-stdlib=libc++"]
    extra_link_args += ["-stdlib=libc++"]

    # The default compiler that ships with Macs doesn't support OpenMP multi-
    # threading. We recommend using the Conda toolchain instead, but will also
    # try to detect if people are using another alternative like Homebrew.

    if "CC" in os.environ:
        extra_compile_args += ["-fopenmp"]
        print(
            "Attempting Pandana compilation with OpenMP multi-threading "
            "support, with user-specified compiler:\n{}".format(os.environ["CC"])
        )

    # Otherwise, if the default clang has been replaced but nothing specified
    # in the 'CC' environment variable, assume they've followed our instructions
    # for using the Conda toolchain.

    elif os.popen("which clang").read().strip() != "/usr/bin/clang":
        cc = "clang"
        cc_catalina = (
            "clang --sysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
        )

        extra_compile_args += ["-fopenmp"]
        print(
            "Attempting Pandana compilation with OpenMP multi-threading "
            "support, with the following compiler:\n{}".format(
                os.popen("which clang").read()
            )
        )

        if " 10.15" in os.popen("sw_vers").read():
            os.environ["CC"] = cc_catalina
        elif " 10." in os.popen("sw_vers").read():  # 10.14 and earlier
            os.environ["CC"] = cc
        else:  # 11.x, 12.x, etc.
            os.environ["CC"] = cc_catalina

    else:
        print(
            "Attempting Pandana compilation without support for "
            "multi-threading. See installation instructions for alternative "
            "options"
        )

# Window compilation: flags are for Visual C++

elif sys.platform.startswith("win"):  # Windows
    extra_compile_args = ["/w", "/openmp", "/std:c++17"]

# Linux compilation: flags are for gcc 4.8 and later

else:  # Linux
    extra_compile_args += ["-fopenmp"]
    extra_link_args += ["-lgomp"]


cyaccess = Extension(
    name='pandana.cyaccess',
    sources=[
        'src/accessibility.cpp',
        'src/graphalg.cpp',
        'src/cyaccess.pyx',
        'src/contraction_hierarchies/src/libch.cpp'],
    language='c++',
    include_dirs=['.', np.get_include()],
    define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_20_API_VERSION")],
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args)


###############################################
# Standard setup
###############################################

version = "0.7"

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    packages=packages,
    name="pandana",
    author="UrbanSim Inc.",
    version=version,
    license="AGPL-3.0-or-later",
    python_requires=">=3.10",
    description=("Python library for network analysis"),
    long_description=(
        "Pandana is a Python library for network analysis that uses "
        "contraction hierarchies to calculate super-fast travel "
        "accessibility metrics and shortest paths. The numerical "
        "code is in C++."
    ),
    url="https://udst.github.io/pandana/",
    ext_modules=[cyaccess],
    install_requires=[
        'numpy >=1.26',
        'pandas >=2.2',
        'requests >=2.0',
        'scikit-learn >=1.5',
        'tables >=3.10'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
