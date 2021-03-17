Change log
==========

v0.6.1
------

2021/03/17

* Adds support for non-x86 CPUs, including ARM-based Macs
* Removes accommodations for pre-C++11 compilers
* Formally ends support for Python 2.7

v0.6
----

2020/11/20

* Adds vectorized, multi-threaded `calculation of many shortest path routes <network.html#pandana.network.Network.shortest_paths>`_ at once
* Restores usability of `network.plot() <network.html#pandana.network.Network.plot>`_ by eliminating usage of Matplotlib's deprecated Basemap toolkit

v0.5.1
------

2020/08/05

* Fixes a performance regression in `network.get_node_ids() <network.html#pandana.network.Network.get_node_ids>`_

v0.5
----

2020/07/28

* Adds support for `calculating shortest path distances <network.html#pandana.network.Network.shortest_path_lengths>`_ between arbitrary origins and destinations, with vectorization and multi-threading
* Restores alternate names for aggregation types, which were inadvertently removed in v0.4
* Fixes a bug with matplotlib backends
* Improves compilation in MacOS 10.15 Catalina
* Makes matplotlib and osmnet dependencies optional
* Revises the documentation and demo notebook

v0.4.4
------

2019/9/4

* Restores support for pre-C++11 compilers.

v0.4.3
------

2019/8/28

* Improved compiler support.

v0.4.2
------

2019/8/8

* Speed of network aggregations is improved.
* Support for aggregating integer values is restored.
* Thread count and contraction hierarchy status messages are restored.
* Code written for v0.3 will continue to run, now raising deprecation warnings instead of errors.
* Compilation improvements for Mac.

v0.4.1
------

2018/7/30

* Documentation fixes.
* Replaced uses of std::map::at() since it's not supported in pre-C++11 compilers.
* Replaced initialization lists due to the same reason as above.

v0.4
----

2017/6/27

* Major rewrite of the layer between Python and C++, which was previously written using the numpy C++ API, and now is written in cython.
* The C++ that remains has been cleaned up a bit and formatted.
* The major functionality change is that global memory is no longer used, so reserve_num_graphs no longer needs to be called and Network objects can be created and destroyed at the user's pleasure.
* The change in global memory made the calls to init_pois no longer necessary. Then, that method has been removed and the max_items and max_distance parameters were relocated in the set_pois call.
* The nearest neighbor queries are now resolved with Scipy instead of libANN. That removed additional global memory.

v0.3
----

2017/4/5

* Python 3 compatibility.
* The “network.nearest_pois()” method can now return the labels of the pois rather than just the distances
* OSM data loading is now done via the osmnet package.
* Changes to support multiple graphs.
* Added reindex functions.
* Updated documentation.
* Switched code style checker in Travis CI to “pycodestyle”, which has replaced the “pep8” package.
