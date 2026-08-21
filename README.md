![Coverage Status](https://img.shields.io/badge/coverage-90%25-green)

# Pandana

Pandana is a Python library for network analysis that uses [contraction hierarchies](https://en.wikipedia.org/wiki/Contraction_hierarchies) to calculate super-fast travel accessibility metrics and shortest paths. The numerical code is in C++.

## Project scope

**Status:** LTS / Compatibility

**Mission:** Pandana provides the established UDST network-accessibility and
shortest-path API for existing applications and users.

**Architecture:** Pandana retains its established CPU and native-code reference
execution architecture as part of its compatibility mission. Architectural
rewrites are outside normal LTS maintenance and require broader scope review.

The project focuses on:

- compatibility with supported Python and scientific Python releases;
- reliable installation and binary packaging;
- correctness and security fixes;
- preservation of established Pandana APIs and behavior; and
- documentation needed to support existing applications.

Pandana is maintained as a stable compatibility library within UDST.
Continuing development of general-purpose network accessibility functionality
takes place in [Pandarm](https://github.com/oturns/pandarm).

Changes that improve reliability, compatibility, and maintainability are
welcome within this mission and architecture. Material changes to the
project's mission or execution architecture are considered through UDST's
organization-level governance process.

See the [UDST Project Directory](https://github.com/UDST/.github/blob/main/PROJECTS.md)
for organization-wide project status and policy.

New in v0.8 is support for current versions of Python (3.10 to 3.14), NumPy 2, and Pandas 3, with binary installers for all platforms built and tested automatically, and OpenMP multithreading on Macs for the first time.

New in v0.5 and v0.6 is vectorized, multi-threaded calculation of shortest path routes and distances: [network.shortest_paths()](http://udst.github.io/pandana/network.html#pandana.network.Network.shortest_paths), [network.shortest_path_lengths()](http://udst.github.io/pandana/network.html#pandana.network.Network.shortest_path_lengths).

Documentation: http://udst.github.io/pandana


### Installation

Binary installers are provided for Mac, Linux, and Windows through both PyPI and Conda Forge.

- `pip install pandana`
- `conda install pandana --channel conda-forge`

Pandana v0.8 supports Python 3.10 to 3.14. The last version with Python 3.8 and 3.9 binaries is v0.7.

See the documentation for information about other [installation options](http://udst.github.io/pandana/installation.html).


### Demo

[Pandana-demo.ipynb](examples/Pandana-demo.ipynb)


### Origins and acknowledgments

Pandana originated in research led by [Paul Waddell](https://github.com/waddell) at the University of California, Berkeley. Waddell conceived the network-accessibility application with [Fletcher Foti](https://github.com/fscottfoti), then his doctoral student and graduate student researcher, and [Dennis Luxen](https://github.com/DennisOSRM) of the Karlsruhe Institute of Technology, and directed and funded the initial development.

Foti led implementation of the original Pandana software and its pandas-oriented interface. Luxen contributed contraction-hierarchy expertise and code developed through the [Open Source Routing Machine project](https://github.com/DennisOSRM/Project-OSRM). Initial development was supported in part by National Science Foundation award [IIS-0964412](https://www.nsf.gov/awardsearch/showAward?AWD_ID=0964412), for which Waddell was the UC Berkeley principal investigator, and by the Metropolitan Transportation Commission.

Subsequent development has included major contributions from [Matt Davis](https://github.com/jiffyclub), [Federico Fernandez](https://github.com/federicofernandez), [Sam Maurer](https://github.com/smmaurer), [Joaquim Gromicho](https://github.com/gromicho), [Eli Knaap](https://github.com/knaaptime), and other community contributors. See the [project history](HISTORY.md) for additional context. The Git history remains the authoritative record of individual code contributions.


### Academic literature

A [paper on Pandana](http://onlinepubs.trb.org/onlinepubs/conferences/2012/4thITM/Papers-A/0117-000062.pdf) by Fletcher Foti, Paul Waddell, and Dennis Luxen was presented at the Transportation Research Board Conference on Innovations in Travel Modeling in 2012. Please cite this paper when referring to the methodology implemented by this library.


### Related UDST libraries

- [OSMnet](https://github.com/udst/osmnet)
- [UrbanAccess](https://github.com/udst/urbanaccess)
