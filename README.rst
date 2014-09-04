Pandana
=======

.. image:: https://travis-ci.org/synthicity/pandana.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/synthicity/pandana

.. image:: https://img.shields.io/coveralls/synthicity/pandana.svg
   :alt: Coverage Status
   :target: https://coveralls.io/r/synthicity/pandana

A nice slideshow showing example code is available
`here <http://bit.ly/1tivyjw>`__.

In this case, a picture is worth a thousand words. The image below shows
the distance to the *2nd* nearest restaurant (rendered by matplotlib)
for the city of San Francisco. With only a few lines of code, you can
grab a network from OpenStreetMap, take the restaurants that users of
OpenStreetMap have recorded, and in about half a second of compute time
you can get back a Pandas Series of node\_ids and computed values of
various measures of access to destinations on the street network.

.. figure:: https://raw.githubusercontent.com/synthicity/pandana/master/docs/img/distance_to_restaurants.png
   :alt: Distance to Restaurants
   :width: 800

   Distance to Restaurants

Beyond simple access to destination queries, this library also
implements more general aggregations along the street network (or any
network). For a given region, this produces hundreds of thousands of
overlapping buffer queries (still performed in less than a second) that
can be used to characterize the local neighborhood around each street
intersection. The result can then be mapped, or assigned to parcel and
building records, or used in statistical models as we commonly do with
`UrbanSim <https://github.com/synthicity/urbansim>`__. This is in stark
contrast to the arbitrary non-overlapping geographies ubiquitous in GIS.
Although there are advantages to the GIS approach, we think network
queries are a more accurate representation of how people interact with
their environment.

We look forward to creative uses of a general library like this - please
let us know when you think you have a great use case with the hashtag
``#synthicity``.

Docs
----

`Documentation <http://synthicity.github.io/pandana>`__ for Pandana is
now available.

Thorough `API
documentation <http://synthicity.github.io/pandana/network.html>`__ for
Pandana is also available.

Acknowledgments
---------------

None of this would be possible without the help of Dennis Luxen (now at
MapBox) and his OSRM (https://github.com/DennisOSRM/Project-OSRM). Thank
you Dennis!

Nearest neighbor queries are performed with the fastest k-d tree around,
i.e. ANN (http://www.cs.umd.edu/~mount/ANN/).

Academic Literature
-------------------

I'm currently working on getting a `complete description of the
methodology <https://github.com/fscottfoti/dissertation/blob/master/networks/Foti%20and%20Waddell%20-%20Accessibility%20Framework.pdf?raw=true>`__
published in an academic journal. Please cite this paper when referring
to the methodology implemented by this library.
