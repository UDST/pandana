[![Coverage Status](https://coveralls.io/repos/github/UDST/pandana/badge.svg?branch=master)](https://coveralls.io/github/UDST/pandana?branch=master)

# Pandana

Pandana is a Python library for network analysis that uses [contraction hierarchies](https://en.wikipedia.org/wiki/Contraction_hierarchies) to calculate super-fast travel accessibility metrics and shortest paths. The numerical code is in C++.

New in v0.5 and v0.6 is vectorized, multi-threaded calculation of shortest path routes and distances: [network.shortest_paths()](http://udst.github.io/pandana/network.html#pandana.network.Network.shortest_paths), [network.shortest_path_lengths()](http://udst.github.io/pandana/network.html#pandana.network.Network.shortest_path_lengths). 

Documentation: http://udst.github.io/pandana


### Installation

As of March 2021, binary installers are provided for Python 3.5 through 3.9 on Mac, Linux, and Windows.

You can install Pandana v0.6 with Pip (Python 3.5 to 3.9):

`pip install pandana`

Or with Conda (Python 3.6 to 3.9):

`conda install pandana --channel conda-forge`


### Demo

[Pandana-demo.ipynb](examples/Pandana-demo.ipynb)


### Acknowledgments

Pandana was created by [Fletcher Foti](https://github.com/fscottfoti), with subsequent contributions from [Matt Davis](https://github.com/jiffyclub), [Federico Fernandez](https://github.com/federicofernandez), [Sam Maurer](https://github.com/smmaurer), and others. Sam Maurer is currently the lead maintainer. Pandana relies on contraction hierarchy code from [Dennis Luxen](https://github.com/DennisOSRM) and his [OSRM project](https://github.com/DennisOSRM/Project-OSRM).


### Academic literature

A [paper on Pandana](http://onlinepubs.trb.org/onlinepubs/conferences/2012/4thITM/Papers-A/0117-000062.pdf) was presented at the Transportation Research Board Annual Conference in 2012. Please cite this paper when referring to the methodology implemented by this library.


### Related UDST libraries

- [OSMnet](https://github.com/udst/osmnet)
- [UrbanAccess](https://github.com/udst/urbanaccess)
