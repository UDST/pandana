![Version](https://img.shields.io/badge/version-0.4.4-blue.svg)
[![Travis build status](https://travis-ci.org/UDST/pandana.svg?branch=master)](https://travis-ci.org/UDST/pandana)
[![Appveyor build status](https://ci.appveyor.com/api/projects/status/a90kvns7qe56kg57?svg=true)](https://ci.appveyor.com/project/smmaurer/pandana)
[![Coverage Status](https://coveralls.io/repos/github/UDST/pandana/badge.svg?branch=master)](https://coveralls.io/github/UDST/pandana?branch=master)

# Pandana

Pandana is a Python package that uses [contraction hierarchies](https://en.wikipedia.org/wiki/Contraction_hierarchies) to perform rapid network calculations including shortest paths and accessibility buffers. The computations are parallelized for use on multi-core machines using an underlying C/C++ library. Pandana is tested on Mac, Linux, and Windows with Python 2.7, 3.6, and 3.7.

Documentation: http://udst.github.io/pandana


### Installation

The easiest way to install Pandana is using the [Anaconda](https://www.anaconda.com/distribution/) package manager. Pandana's Anaconda distributions are pre-compiled and include multi-threading support on all platforms. 

`conda install pandana --channel conda-forge`

See the documentation for information about other [installation options](http://udst.github.io/pandana/installation.html).


### Demo

[Example.ipynb](https://github.com/UDST/pandana/blob/master/examples/Example.ipynb)

The image below shows the distance to the _second_ nearest restaurant from each street intersection in the city of San Francisco. Pandana can calculate this in about half a second of computation time. 

<img src="https://raw.githubusercontent.com/udst/pandana/master/docs/img/distance_to_restaurants.png" width=400>


## Acknowledgments

None of this would be possible without the help of Dennis Luxen and
his [OSRM](https://github.com/DennisOSRM/Project-OSRM) project. Thank you Dennis!


### Academic Literature

A [complete description of the
methodology](http://onlinepubs.trb.org/onlinepubs/conferences/2012/4thITM/Papers-A/0117-000062.pdf)
was presented at the Transportation Research Board Annual Conference in 2012. Please cite this paper when referring
to the methodology implemented by this library.


### Related UDST libraries

- [OSMnet](https://github.com/udst/osmnet)
- [UrbanAccess](https://github.com/udst/urbanaccess)
