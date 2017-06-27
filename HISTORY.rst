v0.4.0
======

2017/6/27

* Major rewrite of the layer between Python and C++, which was previously written using the numpy C++ API, and now is written in cython.
* The C++ that remains has been cleaned up a bit and formatted.
* The major functionality change is that global memory is no longer used, so reserve_num_graphs no longer needs to be called and Network objects can be created and destroyed at the user's pleasure.
* The change in global memory made the calls to init_pois no longer necessary. Then, that method has been removed and the max_items and max_distance parameters were relocated in the set_pois call.
* The nearest neighbor queries are now resolved with Scipy instead of libANN. That removed additional global memory.
