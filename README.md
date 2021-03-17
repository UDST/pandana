![Coverage Status](https://img.shields.io/badge/coverage-90%25-green)

# Pandana

Pandana is a Python library for network analysis that uses [contraction hierarchies](https://en.wikipedia.org/wiki/Contraction_hierarchies) to calculate super-fast travel accessibility metrics and shortest paths. The numerical code is in C++.

New in v0.5 and v0.6 is vectorized, multi-threaded calculation of shortest path routes and distances: [network.shortest_paths()](http://udst.github.io/pandana/network.html#pandana.network.Network.shortest_paths), [network.shortest_path_lengths()](http://udst.github.io/pandana/network.html#pandana.network.Network.shortest_path_lengths). 

Documentation: http://udst.github.io/pandana


### Installation

As of March 2021, binary installers are provided for Mac, Linux, and Windows through both PyPI and Conda Forge. 

- `pip install pandana`
- `conda install pandana --channel conda-forge`

Pandana works best in Python 3.6+, although binary installers for Python 3.5 remain available on Pip. The last version of Pandana with Python 2.7 binaries is v0.4.4 on Conda Forge.

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
