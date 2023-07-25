Installation
============

Pandana is a Python package that includes a C++ extension for numerical operations. 


Standard installation
------------------------------

As of March 2021, binary installers are provided for Mac, Linux, and Windows through both PyPI and Conda Forge.

You can install Pandana using Pip::

    pip install pandana

Or Conda::

    conda install pandana --channel conda-forge

Pandana is easiest to install in Python 3.8 to 3.11. The last version of Pandana with Python 2.7 binaries is v0.4.4 on Conda Forge. The last version with Python 3.5 binaries is v0.6 on Pip.


ARM-based Macs
------------------------------

Native binary installers for ARM-based Macs are available on Conda Forge, but to use these your full Python stack needs to be optimized for ARM. 

If you're running Python through Rosetta translation (which is the default), older Mac installers will continue to work fine. See `issue #152 <https://github.com/UDST/pandana/issues/152>`_ for tips and further discussion.


Compiling from source code
------------------------------

You may want to compile Pandana locally if you're modifying the source code or need to use a version that's missing binary installers for your platform.

Mac users should start by running ``xcode-select --install`` to make sure you have Apple's Xcode command line tools, which are needed behind the scenes. Windows users will need the `Microsoft Visual C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_.

Pandana's build-time requirements are ``cython``, ``numpy``, and a C++ compiler that supports the C++11 standard. Additionally, the compiler needs to support OpenMP to allow Pandana to use multithreading.

The smoothest route is to get the compilers from Conda Forge -- you want the ``clang`` and ``llvm-openmp`` packages. Running Pandana's setup script will trigger compilation::

    conda install cython numpy clang llvm-openmp
    python setup.py develop

You'll see a lot of status messages go by, but hopefully no errors.

MacOS 10.14 (but not newer versions) often needs additional header files installed. If you see a compilation error like ``'wchar.h' file not found`` in MacOS 10.14, you can resolve it by running this command::

    open /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg


Advanced compilation tips
------------------------------

If you prefer not to use Conda, you can skip the ``clang`` and ``llvm-openmp`` packages. Compilation will likely work fine with your system's built-in toolchain. 

The default C++ compiler on Macs doesn't support OpenMP, though, meaning that Pandana won't be able to use multithreading.

You can set the ``CC`` environment variable to specify a compiler of your choice. See writeup in `PR #137 <https://github.com/UDST/pandana/pull/137>`_ for discussion of this. If you need to make additional modifications, you can edit the compilation script in your local copy of ``setup.py``.


Multithreading
------------------------------

You can check how many threads Pandana is able to use on your machine by running the ``examples/simple_example.py`` script.
