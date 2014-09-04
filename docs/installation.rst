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
* `pandas`_ >= 0.13.1
* `tables`_ >= 3.1.0

Install the latest release
--------------------------

.. note::
   Installing via conda or pip on a Mac will install Pandana without
   multithreading support.
   See instructions below for installing on a Mac with multithreading
   support.

conda
~~~~~

Pandana and some of its dependencies are hosted on
`Synthicity's binstar repository <https://binstar.org/synthicity>`__.
To add this as a default installation channel for conda run this code
in a terminal::

    conda config --add channels synthicity

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

* Clone the `pandana repo <https://github.com/synthicity/pandana>`__
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

Our you can get the `development repository <https://github.com/synthicity/pandana>`__
and run ``python setup.py install``.

After installation, executing :code:`examples/simple_example.py` will print out the
number of threads that are being utilized.  If Pandana says it is using 1
thread, and your computer has multiple cores, Pandana is not installed
correctly.  Check the compile output for the gcc compiler you specified
with :code:`CC` and :code:`CXX` - you might need to change the name slightly depending
on your platform - for instance :code:`g++-mp-4.9` or :code:`g++-4.8`.

.. _Anaconda: http://docs.continuum.io/anaconda/
.. _pip: https://pip.pypa.io/en/latest/
.. _OpenMP: http://openmp.org/wp/
.. _GNU GCC: https://gcc.gnu.org/
.. _Homebrew: http://brew.sh/
.. _MacPorts: https://www.macports.org/
.. _brewer2mpl: https://github.com/jiffyclub/brewer2mpl/wiki
.. _matplotlib: http://matplotlib.org/
.. _numpy: http://www.numpy.org/
.. _pandas: http://pandas.pydata.org/
.. _tables: http://www.pytables.org/
