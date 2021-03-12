Installation
============

Pandana is a Python package that includes a C++ extension for numerical operations. As of March 2021, binary installers are provided for Python 3.5 through 3.9 on Mac, Linux, and Windows.


Standard installation
------------------------------

You can install Pandana with Pip (Python 3.5 to 3.9)::

    pip install pandana

Or with Conda (Python 3.6 to 3.9)::

    conda install pandana --channel conda-forge


ARM-based Macs
------------------------------

Pandana's binary installers are optimized for x86 (Intel) Macs from 2020 and earlier, but will also run on newer ARM-based Macs.

If you'd like to compile Pandana locally for ARM, see instructions in `issue #152 <https://github.com/UDST/pandana/issues/152>`_. In our testing, natively compiled binaries run about 35% faster than the x86 binaries with Rosetta translation. We aim to provide osx-arm64 binaries on Pip and Conda as soon as it's feasible.


Compiling from source code
------------------------------

You may want to compile Pandana locally if you're modifying the source code or need to use a version that's missing binary installers for your platform.

Mac users should start by running ``xcode-select --install`` to make sure you have Apple's Xcode command line tools, which are needed behind the scenes. Windows users will need the `Microsoft Visual C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_.

Pandana's build-time requirements are ``cython``, ``numpy``, and a C++ compiler that supports the c++11 standard. Additionally, the compiler needs to support OpenMP to allow Pandana to use multithreading.

The smoothest route is to get the compilers from Conda Forge -- you want the ``clang`` and ``llvm-openmp`` packages. Running Pandana's setup script will trigger compilation::

    conda install cython numpy clang llvm-openmp
    python setup.py develop

You'll see a lot of status messages go by, but hopefully no errors.

MacOS 10.14 (but not later versions) often needs additional header files installed. If you see a compilation error like ``'wchar.h' file not found`` in MacOS 10.14, you can resolve it by running this command::

    open /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg


Advanced compilation tips
------------------------------

If you prefer not to use Conda, you can skip the ``clang`` and ``llvm-openmp`` packages. Compilation will likely work fine with your system's built-in toolchain. 

The default C++ compiler on Macs doesn't support OpenMP, though, meaning that Pandana won't be able to use multithreading.

You can set the ``CC`` environment variable to specify a compiler of your choice. See writeup in `PR #137 <https://github.com/UDST/pandana/pull/137>`_ for discussion of this. If you need to make additional modifications, you can edit the compilation script in your local copy of ``setup.py``.


Multithreading
------------------------------

You can check how many threads Pandana is able to use on your machine by running the ``examples/simple_example.py`` script.
