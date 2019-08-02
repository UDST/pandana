Installation
============

Pandana depends on a number of libraries from the scientific Python stack.
The easiest way to get these is to use the `Anaconda`_ python distribution,
and the instructions below will assume you are using Anaconda.

Dependencies
------------

Pandana depends on the following libraries, most of which are in Anaconda:

* `brewer2mpl`_ >= 1.4
* `matplotlib`_ >= 1.3.1
* `numpy`_ >= 1.8.0
* `pandas`_ >= 0.17.0
* `tables`_ >= 3.1.0
* `osmnet`_ >= 0.1.0

Install the latest release
--------------------------

.. note::
   Installing via conda or pip on a Mac will install Pandana without
   multithreading support.
   See instructions below for installing on a Mac with multithreading
   support.

conda
~~~~~

Pandana is hosted on
`UDST's Anaconda repository <https://anaconda.org/udst>`__. Other dependencies
can be installed through the ``conda-forge`` channel.
To add these as default installation channels for conda, run this code
in a terminal::

    conda config --add channels udst
    conda config --add channels conda-forge

Then you can install pandana::

    conda install pandana

To update pandana to a new release, run::

    conda update pandana

pip
~~~

Pandana is available on PyPI and can be installed with::

    pip install -U pandana

On Windows and Mac this will install binary builds, assuming you are using
a recent version of `pip`_. On Linux it will perform a source install.

Development Installation
------------------------

* Clone the `pandana repo <https://github.com/udst/pandana>`__
* Run ``python setup.py develop``

(This is a C extension so requires C/C++ compilers, but should compile on
Linux, Windows, and Mac.)

Multithreaded Installation on Mac
---------------------------------

The default compilers on Mac do not support `OpenMP`_ (which we use to
parallelize the computations).
To get multithreaded Pandana on Mac you'll need to install `GNU GCC`_
and then compile Pandana from source.
The easiest way to get GCC is via `Homebrew`_ or `MacPorts`_:

* Homebrew: ``brew install gcc``
* MacPorts: ``port install gcc``

Then you must specify the GCC compilers for use during compilation
via environment variables and tell the ``setup.py`` script explicitly
to build with OpenMP::

    export CC=gcc-4.9
    export CXX=g++-4.9
    export USEOPENMP=1

.. note::

   The value of the variables you set will depend on the
   exact version of GCC installed.

To install the latest release from source using `pip`_::

    pip install -U --no-use-wheel pandana

Our you can get the `development repository <https://github.com/udst/pandana>`__
and run ``python setup.py install``.

After installation, executing :code:`examples/simple_example.py` will print out the
number of threads that are being utilized.  If Pandana says it is using 1
thread, and your computer has multiple cores, Pandana is not installed
correctly.  Check the compile output for the gcc compiler you specified
with :code:`CC` and :code:`CXX` - you might need to change the name slightly depending
on your platform - for instance :code:`g++-mp-4.9` or :code:`g++-4.8`.

Installation on Windows
-----------------------
`Microsoft Visual C++ 2008 SP1 Redistributable Package (x64) 
<https://www.microsoft.com/en-us/download/details.aspx?id=2092>`_ is required for running 
Pandana on Windows.  This package enables parallel computations with `OpenMP`_.  Building Pandana 
from source also requires `Microsoft Visual C++ Compiler for Python 2.7 
<https://www.microsoft.com/en-us/download/details.aspx?id=44266>`_.


.. _Anaconda: http://docs.continuum.io/anaconda/
.. _pip: https://pip.pypa.io/en/latest/
.. _OpenMP: http://openmp.org
.. _GNU GCC: https://gcc.gnu.org/
.. _Homebrew: http://brew.sh/
.. _MacPorts: https://www.macports.org/
.. _brewer2mpl: https://github.com/jiffyclub/brewer2mpl/wiki
.. _matplotlib: http://matplotlib.org/
.. _numpy: http://www.numpy.org/
.. _pandas: http://pandas.pydata.org/
.. _tables: http://www.pytables.org/
.. _osmnet: http://github.com/udst/osmnet