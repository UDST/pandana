![Version](https://img.shields.io/badge/version-0.5-blue.svg)
[![Travis build status](https://travis-ci.org/UDST/pandana.svg?branch=master)](https://travis-ci.org/UDST/pandana)
[![Appveyor build status](https://ci.appveyor.com/api/projects/status/a90kvns7qe56kg57?svg=true)](https://ci.appveyor.com/project/smmaurer/pandana)
[![Coverage Status](https://coveralls.io/repos/github/UDST/pandana/badge.svg?branch=master)](https://coveralls.io/github/UDST/pandana?branch=master)

# Pandana

Pandana is a Python library for network analysis that uses [contraction hierarchies](https://en.wikipedia.org/wiki/Contraction_hierarchies) to calculate super-fast travel accessibility metrics and shortest paths. The numerical code is in C++.

v0.5 adds vectorized calculation of shortest path lengths: [network.shortest_path_lengths()](http://udst.github.io/pandana/network.html#pandana.network.Network.shortest_path_lengths). 

Documentation: http://udst.github.io/pandana


### Installation

Pandana runs on Mac, Linux, and Windows with Python 2.7, 3.6, 3.7, and 3.8.

The easiest way to install Pandana is using the [Anaconda](https://www.anaconda.com/distribution/) package manager. Pandana's Anaconda distributions are pre-compiled and include multi-threading support on all platforms. 

`conda install pandana --channel conda-forge`

See the documentation for information about other [installation options](http://udst.github.io/pandana/installation.html).


### Demo

[Pandana-demo.ipynb](examples/Pandana-demo.ipynb)



### Acknowledgments

Pandana was created by [Fletcher Foti](https://github.com/fscottfoti), with subsequent contributions from [Matt Davis](https://github.com/jiffyclub), [Federico Fernandez](https://github.com/federicofernandez), [Sam Maurer](https://github.com/smmaurer), and others. Sam Maurer is currently the lead maintainer. Pandana relies on contraction hierarchy code from [Dennis Luxen](https://github.com/DennisOSRM) and his [OSRM project](https://github.com/DennisOSRM/Project-OSRM).


### Academic literature

A [paper on Pandana](http://onlinepubs.trb.org/onlinepubs/conferences/2012/4thITM/Papers-A/0117-000062.pdf) was presented at the Transportation Research Board Annual Conference in 2012. Please cite this paper when referring to the methodology implemented by this library.


### Related UDST libraries

- [OSMnet](https://github.com/udst/osmnet)
- [UrbanAccess](https://github.com/udst/urbanaccess)
