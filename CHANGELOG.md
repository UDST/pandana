v0.8.1
======

2026/11/18 (release candidate 1)

* `Network()` now raises a `ValueError` if any edge refers to a node ID that isn't in the node table. Previously the network was built without complaint, with the edge attached to the wrong node
* Reduces memory use for large networks and queries by storing node indices as 32-bit integers inside the compiled extension; node IDs remain 64-bit. `Network()` raises a `ValueError` if there are more nodes than a 32-bit index can address (about 2.1 billion)
* The warning from `Network.shortest_path_lengths()` about unconnected node pairs now reports how many there are and lists up to 10 of them, rather than every pair, which could exhaust memory for large batches. The wording of the warning has changed. Also fixes a `KeyError` when node IDs are passed as Series with a non-default index
* For code that uses Pandana's internals: `Network.node_idx` is now `int32`, and the `pandana.cyaccess` methods that take internal node indices require `int32` arrays
* Adds binary installers for Python 3.15. Until `numexpr` and `ndindex` publish wheels for Python 3.15, pip builds those two dependencies from source there, which requires a C/C++ compiler; Conda Forge is not affected
* Releases are now published to PyPI from GitHub Actions using Trusted Publishing
* Thanks to @gromicho for the shortest-path warning and integer index work (PRs #211 and #215)

v0.8
====

2026/08/24

* Adds support for Python 3.10 to 3.14, NumPy 2, Pandas 3, and Cython 3; drops Python 3.8 and 3.9
* Builds binary installers for all platforms automatically, including Apple Silicon Macs and ARM Linux, and tests each one before release
* Fixes failures on Windows caused by 32-bit `long` integers in the compiled extension, by using explicit 64-bit integer types
* Improves support for network files saved with older versions of Pandas: `Network.from_hdf5()` reads them directly when the installed Pandas can, and otherwise accepts `migrate_legacy=True`; adds `pandana.loaders.pandash5.open_hdf_store()` and `migrate_legacy_hdf()`
* Modernizes the build and test infrastructure, including compatibility testing against the oldest supported dependency versions
* Thanks to @knaaptime (PR #196) and @gromicho (PR #198) for the compatibility work, and to the Pandarm project for the approach to bundling OpenMP in Mac wheels

v0.7
====

2023/07/26

* Adds support for calculating accessibility isochrones: which nodes are within x network distance of a source node
* Allows a maximum distance to be set for POIs
* Adds a warning when a shortest path is requested between unconnected nodes
* Supports PyTables 3.7+
* Support Pandas 2.0
* Switches to pyproject.toml packaging standards
* Adds binaries on PyPI to support Python 3.10 and 3.11
* Improves compilation in MacOS 12+

v0.6.1
======

2021/03/17

* Adds support for non-x86 CPUs, including ARM-based Macs
* Removes accommodations for pre-C++11 compilers
* Formally ends support for Python 2.7

v0.6
====

2020/11/20

* Adds vectorized, multi-threaded calculation of many shortest path routes at once
* Restores usability of network.plot() by eliminating usage of Matplotlib's deprecated Basemap toolkit

v0.5.1
======

2020/08/05

* Fixes a performance regression in network.get_node_ids()

v0.5
====

2020/07/28

* Adds support for calculating shortest path distances between arbitrary origins and destinations, with vectorization and multi-threading
* Restores alternate names for aggregation types, which were inadvertently removed in v0.4
* Fixes a bug with matplotlib backends
* Improves compilation in MacOS 10.15 Catalina
* Makes matplotlib and osmnet dependencies optional
* Revises the documentation and demo notebook

v0.4.4
======

2019/9/4

* Restores support for pre-C++11 compilers.

v0.4.3
======

2019/8/28

* Improved compiler support.

v0.4.2
======

2019/8/8

* Speed of network aggregations is improved.
* Support for aggregating integer values is restored.
* Thread count and contraction hierarchy status messages are restored.
* Code written for v0.3 will continue to run, now raising deprecation warnings instead of errors.
* Compilation improvements for Mac.

v0.4.1
======

2018/7/30

* Documentation fixes.
* Replaced uses of std::map::at() since it's not supported in pre-C++11 compilers.
* Replaced initialization lists due to the same reason as above.

v0.4.0
======

2017/6/27

* Major rewrite of the layer between Python and C++, which was previously written using the numpy C++ API, and now is written in cython.
* The C++ that remains has been cleaned up a bit and formatted.
* The major functionality change is that global memory is no longer used, so reserve_num_graphs no longer needs to be called and Network objects can be created and destroyed at the user's pleasure.
* The change in global memory made the calls to init_pois no longer necessary. Then, that method has been removed and the max_items and max_distance parameters were relocated in the set_pois call.
* The nearest neighbor queries are now resolved with Scipy instead of libANN. That removed additional global memory.

v0.3.0
======

2017/4/5

* Python 3 compatibility.
* The “network.nearest_pois()” method can now return the labels of the pois rather than just the distances
* OSM data loading is now done via the osmnet package.
* Changes to support multiple graphs.
* Added reindex functions.
* Updated documentation.
* Switched code style checker in Travis CI to “pycodestyle”, which has replaced the “pep8” package.
