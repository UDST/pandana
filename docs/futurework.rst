Planned Improvements
--------------------

As has been shown, the main use case for Pandana is to expose the
functionality of an underlying C++ library using a simple Python API,
in a sense getting the best characteristics of both languages.  It's worth
noting that there is
additional functionality already implemented in the C++ library which has not
been exposed, tested, and documented at this time, but would require moderate
effort
to do so and which will certainly be done in the future.  This functionality
includes:

* Batch (multi-threaded) routing between a large number of pairs of nodes in
  the network

* Additional OpenStreetMap, ESRI ShapeFile and Geodatabase,
  and GTFS (General Transit Feed Service) importing

* Unification of multiple networks, like combining the pedestrian
  OpenStreetMap network with the GTFS transit schedules

* Returning a DataFrame of all source-destination nodes within a certain
  distance (and including the distance)

* Design variables of the network, including 4-way street intersections,
  connectivity with the larger network, street length within a radius,
  average street width, and others

* Diversity variables which combine other variables using "mixture" measures
  like entropy, e.g. jobs/housing balance

* Centrality measures (measures which show bottlenecks in the network)

* Sampling nodes within a distance range (generally of use for urban modelling)

* Weighted combinations of multiple attributes, which are used to compute
  logsums in destination choice models.

Please let us know if any of these items are high priority for you and we
will do our best to increase their standing in the task queue.