Installation
------------

Install the latest release
~~~~~~~~~~~~~~~~~~~~~~~~~~

`conda install pandana`

Start using Pandana.

Installation from Source
~~~~~~~~~~~~~~~~~~~~~~~~

* Clone this repo
* run python setup.py install`

(This is a C extension so requires C/C++ compilers, but should compile on
Linux, Windows, and Mac.)

Multithreaded Installation on Mac
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Mac, the default compiler does not support OPENMP (What we use to
parallelize the computations).  To get multithreaded Pandana on mac.

* Make sure you have gcc - the easiest way is via `brew install gcc49` or
  `port install gcc49`

* `export CC=g++-4.9`

* `export CXX=g++-4.9`

* `python setup.py install`

* After installation, executing `examples/simple_example.py` will print out the
  number of threads that are being utilized.  If Pandana says it is using 1
  thread, and your computer has multiple cores, Pandana is not installed
  correctly.  Check the compile output for the gcc compiler you specified
  with `CC` and `CXX` - you might need to change the name slightly depending
  on your platform - for instance `g++-mp-4.9` or `g++-4.8`.
