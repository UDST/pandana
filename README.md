Pandana
=======

[![Build Status](https://travis-ci.org/synthicity/pandana.svg?branch=master)](https://travis-ci.org/synthicity/pandana) [![Coverage Status](https://img.shields.io/coveralls/synthicity/pandana.svg)](https://coveralls.io/r/synthicity/pandana)

![Distance to Restaurants](https://raw.githubusercontent.com/synthicity/pandana/master/docs/_static/distance_to_restaurants.png)

In this case, a picture is worth a thousand words.  Here is shown the distance to the *2nd* nearest restaurant in matplotlib.  With only a few lines of code, you can grab a network from OpenStreetMap, take the restaurants that users of OpenStreetMap have recorded, and in about half a second of compute time you can get back a Pandas Series of node_ids and computed values of various measures of access to destinations on the street network.

Beyond simple access to destination queries, this library also implements more general aggregations along the street network (or any network).  For a given region, this produces hundreds of thousands of overlapping buffer queries (still performed in less than a second) that can be used to characterize the local neighborhood around each street intersection.  The result can then be mapped, or assigned to parcel or building records, or used in statistical models as we commonly do with [UrbanSim](https://github.com/synthicity/urbansim).  This is in stark contrast to the arbitrary non-overlapping geographies ubiquitous in GIS.  Although there are advantages to the GIS approach, we think network queries are a more accurate representation of how people interact with their environment.

Acknowledgments
==============

None of this would be possible without the help of Dennis Luxen (now at MapBox) and his OSRM (https://github.com/DennisOSRM/Project-OSRM).  Thank you Dennis!

Nearest neighbor queries are performed with the fastest k-d tree around, i.e. ANN (http://www.cs.umd.edu/~mount/ANN/).

Academic Literature
===================
I'm currently working on getting a [complete description fo the methodology](https://github.com/fscottfoti/dissertation/blob/master/networks/Foti%20and%20Waddell%20-%20Accessibility%20Framework.pdf?raw=true) published in an academic journal.  Please cite this paper when referring to the methodology implemented by this library.

Install
=======

Clone this repo and run `python setup.py install`. Requires C/C++ compilers.

Docs
====

[Documentation](http://synthicity.github.io/pandana/network.html) for Pandana is now available.

Thorough [API documentation](http://synthicity.github.io/pandana/network.html) for Pandana is also available.
