Installation
============

Pandana is a Python package that includes a C++ extension for numerical operations. Pandana is tested on Mac, Linux, and Windows with Python 2.7, 3.6, 3.7, and 3.8.

The easiest way to install Pandana is using the `Anaconda`_ package manager. Pandana's Anaconda distributions are pre-compiled and include multi-threading support on all platforms.

If you install Pandana from Pip or from the source code on GitHub, you'll need to compile the C++ components locally. This is automatic, but won't work unless the right build tools are in place. See full instructions below.


Anaconda (recommended!)
------------------------------

Pandana is hosted on Conda Forge::

    conda install pandana --channel conda-forge


.. _pip:

Pip (requires local compilation)
--------------------------------

Pandana is also hosted on PyPI::

    pip install pandana

Pandana's C++ components will compile automatically if the right tools are present. See instructions below for individual operating systems.


.. _github:

GitHub (requires local compilation)
-----------------------------------

If you'll be modifying the code, you can install Pandana from the `GitHub source <https://github.com/udst/pandana>`_::

    git clone https://github.com/udst/pandana.git
    cd pandana
    pip install cython numpy
    python setup.py develop

Pandana's C++ components will compile automatically if the right tools are present. See instructions below for individual operating systems.


Tips for local compilation
--------------------------

If you cannot install using Conda, Pandana's C++ code will need to be compiled locally on your machine.

Compiling in MacOS
~~~~~~~~~~~~~~~~~~

MacOS comes with C++ compilers, but the built-in ones don't allow multi-threading in Pandana. So, run this if possible before installing Pandana from source code::

    xcode-select --install
    conda install cython numpy llvm-openmp clang

Pandana will automatically detect that these are installed, and compile itself with multi-threading enabled. 

If you prefer to use a different compiler, provide a path in the ``CC`` environment variable and we'll use that one instead. See writeup in `PR #137 <https://github.com/UDST/pandana/pull/137>`_ for some more discussion of this.

If you get a compilation error like ``'wchar.h' file not found`` in MacOS 10.14, you can resolve it by installing some additional header files::

    open /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg

Compiling in Linux
~~~~~~~~~~~~~~~~~~

Pandana's setup script expects a version of the GCC compiler with support for OpenMP. This appears to be GCC 4.8+, but we haven't done extensive testing. If you run into problems, try doing a fresh install of the core build tools::

    sudo apt-get install --reinstall build-essential

Compiling in Windows
~~~~~~~~~~~~~~~~~~~~

Compilation is automatic but requires that `Microsoft Visual C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_ are installed.

Certain older machines may need the `Microsoft Visual C++ 2008 SP1 Redistributable Package (x64) <https://www.microsoft.com/en-us/download/details.aspx?id=2092>`_ or something similar in order to use Pandana. This provides runtime components of the Visual C++ libraries.


Multi-threading
---------------

After installing Pandana, running :code:`examples/simple_example.py` will display the number of threads that Pandana is using.

If you're installing from source code on a Mac, see "Compiling in MacOS" above for more information about enabling multi-threading.

.. note::
    The multi-threading status indicator maybe incorrect in certain Windows environments. See GitHub `issue #138 <https://github.com/UDST/pandana/issues/138>`_ for the latest information on this.




.. _Anaconda: https://www.anaconda.com/distribution/
