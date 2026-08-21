Installation
============

Pandana is a Python package that includes a C++ extension for numerical operations.


Standard installation
------------------------------

Binary installers are provided for Mac, Linux, and Windows through both PyPI and Conda Forge.

You can install Pandana using Pip::

    pip install pandana

Or Conda::

    conda install pandana --channel conda-forge

Pandana v0.8 supports Python 3.10 to 3.14. The last version with Python 3.8 and 3.9 binaries is v0.7. The last version with Python 2.7 binaries is v0.4.4 on Conda Forge, and the last version with Python 3.5 binaries is v0.6 on Pip.


Binary installers
------------------------------

Each release includes wheels for these platforms, all built with OpenMP multithreading enabled:

* Linux x86_64 and aarch64
* Mac, Intel and Apple Silicon (requires macOS 15 or later)
* Windows x86_64

The wheels are built and tested by a GitHub Actions workflow. If there's no wheel for your platform, Pip will try to compile Pandana from source, which needs the build tools described below.


Compiling from source code
------------------------------

You may want to compile Pandana locally if you're modifying the source code or need to use a version that's missing binary installers for your platform.

Pandana's build-time requirements are ``cython``, ``numpy``, and a C++ compiler that supports the C++17 standard. Additionally, the compiler needs to support OpenMP to allow Pandana to use multithreading.

On Linux, your system's GCC should be fine. Windows users will need the `Microsoft Visual C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_. Mac users should start by running ``xcode-select --install`` to make sure you have Apple's Xcode command line tools, which are needed behind the scenes.

Running Pandana's setup script will trigger compilation::

    pip install setuptools cython numpy
    pip install --no-build-isolation --editable .

You'll see a lot of status messages go by, but hopefully no errors.


Compiling with OpenMP on a Mac
------------------------------

The default C++ compiler on Macs doesn't include OpenMP, so a plain source build will work but run single-threaded. To get multithreading, use the compilers and OpenMP runtime from Conda Forge. On an Apple Silicon Mac::

    conda install setuptools cython numpy clang_osx-arm64 clangxx_osx-arm64 llvm-openmp
    pip install --no-build-isolation --editable .

On an Intel Mac, use ``clang_osx-64`` and ``clangxx_osx-64`` instead. These packages set the ``CC`` and ``CXX`` environment variables when the Conda environment is active, and Pandana's setup script will detect them and link against OpenMP.

Alternatively, if you prefer Homebrew, ``brew install libomp`` and then build with ``CC=clang`` and ``CPPFLAGS``/``LDFLAGS`` pointing at the libomp install location. This is how the release wheels are built; see ``.github/workflows/build-wheels.yml`` for the details, and the writeup in `PR #137 <https://github.com/UDST/pandana/pull/137>`_ for background on Mac compilers. If you need to make additional modifications, you can edit the compilation script in your local copy of ``setup.py``.


Multithreading
------------------------------

You can check how many threads Pandana is able to use on your machine by running the ``examples/simple_example.py`` script, or ``python tests/check_openmp.py``, which fails if fewer than two threads are available.
