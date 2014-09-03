Installation
------------

Install the latest release
~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`conda install pandana`

Start using Pandana.

Installation from Source
~~~~~~~~~~~~~~~~~~~~~~~~

* Clone this repo
* run :code:`python setup.py install`

(This is a C extension so requires C/C++ compilers, but should compile on
Linux, Windows, and Mac.)

Multithreaded Installation on Mac
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Mac, the default compiler does not support OPENMP (What we use to
parallelize the computations).  To get multithreaded Pandana on mac:

* Make sure you have gcc - the easiest way is via :code:`brew install gcc49` or
  :code:`port install gcc49`

* :code:`export CC=g++-4.9`

* :code:`export CXX=g++-4.9`

* :code:`python setup.py install`

* After installation, executing :code:`examples/simple_example.py` will print out the
  number of threads that are being utilized.  If Pandana says it is using 1
  thread, and your computer has multiple cores, Pandana is not installed
  correctly.  Check the compile output for the gcc compiler you specified
  with :code:`CC` and :code:`CXX` - you might need to change the name slightly depending
  on your platform - for instance :code:`g++-mp-4.9` or :code:`g++-4.8`.
