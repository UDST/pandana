import os
import sys

import numpy as np  # for c++ headers

from setuptools import find_packages, setup, Extension


###############################################
# Building the C++ extension
###############################################

extra_compile_args = ["-w", "-std=c++17", "-O3"]
extra_link_args = []

# Mac compilation: Apple's clang doesn't ship an OpenMP runtime, so
# multithreading needs LLVM's libomp from somewhere else. Three cases:
#
#   1. CC is set: the user chose a compiler, e.g. Homebrew or Conda Forge
#      LLVM clang, or Apple clang with Homebrew libomp (which is what
#      cibuildwheel does). Enable OpenMP in whichever way that compiler
#      supports, honoring any CPPFLAGS/LDFLAGS that point at libomp.
#   2. A non-Apple clang is first on the PATH, e.g. from the Conda Forge
#      'clang' + 'llvm-openmp' packages: use it with -fopenmp.
#   3. Otherwise, build single-threaded with the system compiler.

if sys.platform.startswith("darwin"):  # Mac

    extra_compile_args += ["-stdlib=libc++"]
    extra_link_args += ["-stdlib=libc++"]

    if "CC" in os.environ:
        cc_version = os.popen("{} --version".format(os.environ["CC"])).read()
        if "Apple" in cc_version:
            # Apple clang rejects -fopenmp, but can still build OpenMP code
            # if libomp is installed (e.g. from Homebrew): enable the pragmas
            # in the frontend and link the runtime explicitly. Point CPPFLAGS
            # and LDFLAGS at libomp if it isn't on the default search path.
            extra_compile_args += ["-Xpreprocessor", "-fopenmp"]
            extra_link_args += ["-lomp"]
        else:
            # LLVM clang or GCC: the driver finds its own OpenMP runtime
            extra_compile_args += ["-fopenmp"]
            extra_link_args += ["-fopenmp"]
        print(
            "Attempting Pandana compilation with OpenMP multi-threading "
            "support, with user-specified compiler:\n{}".format(os.environ["CC"])
        )

    elif os.popen("which clang").read().strip() not in ("", "/usr/bin/clang"):
        sdk = os.popen("xcrun --show-sdk-path").read().strip()
        os.environ["CC"] = "clang --sysroot {}".format(sdk) if sdk else "clang"
        extra_compile_args += ["-fopenmp"]
        extra_link_args += ["-fopenmp"]
        print(
            "Attempting Pandana compilation with OpenMP multi-threading "
            "support, with the following compiler:\n{}".format(
                os.popen("which clang").read()
            )
        )

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

version = "0.8"

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    packages=packages,
    name="pandana",
    author="UrbanSim Inc.",
    version=version,
    license="AGPL-3.0-or-later",
    python_requires=">=3.10",
    description=("Python library for network analysis"),
    long_description_content_type="text/x-rst",
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
