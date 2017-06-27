Pandana
=======

.. image:: https://travis-ci.org/UDST/pandana.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/UDST/pandana

.. image:: https://coveralls.io/repos/UDST/pandana/badge.svg?branch=master&service=github
   :alt: Coverage Status
   :target: https://coveralls.io/r/UDST/pandana


In this case, a picture is worth a thousand words. The image below shows
the distance to the *2nd* nearest restaurant (rendered by matplotlib)
for the city of San Francisco. With only a few lines of code, you can
grab a network from OpenStreetMap, take the restaurants that users of
OpenStreetMap have recorded, and in about half a second of compute time
you can get back a Pandas Series of node\_ids and computed values of
various measures of access to destinations on the street network.

.. figure:: https://raw.githubusercontent.com/udst/pandana/master/docs/img/distance_to_restaurants.png
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
`UrbanSim <https://github.com/udst/urbansim>`__. This is in stark
contrast to the arbitrary non-overlapping geographies ubiquitous in GIS.
Although there are advantages to the GIS approach, we think network
queries are a more accurate representation of how people interact with
their environment.

We look forward to creative uses of a general library like this - please
let us know if you think you have a great use case by tweeting us at
``@urbansim`` or post on the UrbanSim `forum`_.

Docs
----

`Documentation <http://udst.github.io/pandana>`__ for Pandana is
now available.

Thorough `API
documentation <http://udst.github.io/pandana/network.html>`__ for
Pandana is also available.

Acknowledgments
---------------

None of this would be possible without the help of Dennis Luxen and
his OSRM (https://github.com/DennisOSRM/Project-OSRM). Thank you Dennis!

Academic Literature
-------------------

A `complete description of the
methodology <http://onlinepubs.trb.org/onlinepubs/conferences/2012/4thITM/Papers-A/0117-000062.pdf>`__
was presented at the Transportation Research Board Annual Conference in 2012. Please cite this paper when referring
to the methodology implemented by this library.

Related UDST libraries
----------------------

-  `OSMnet`_
-  `UrbanAccess`_

.. _forum: http://discussion.urbansim.com/
.. _OSMnet: https://github.com/udst/osmnet
.. _UrbanAccess: https://github.com/UDST/urbanaccess
