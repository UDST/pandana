urbanaccess
===========

Accessibility as defined here is the ability to reach other specified locations in the city.

In practice, it's a bit more subtle than that.  This framework serves to aggregate data along the transportation network in a way that typically creates a smooth surface over the entire city of the variable of interest.

How does this work.  

1) create and preprocess the network

Networks are completely abstract in that they have nodes, edges, and one or more impedances associated with each edge.  Impedances can be time or distance or an index of some kind, but there is a single number associated with each edge.  (If you pass multiple impedances for each edge, a different instance of the network is created for each network.  For instance, for congested travel time by time of day.  Pedestrian, auto, and local street networks have all been used in this framework successfully.

2) assign the variable to the network

First, take the variable of interest.  In some cases it's discrete - like the number of coffee shops, in other cases it's continuous like the income of people.  But you have observations of some kind tied to x-y coordinates in the city.  So you map these to the network, usually be doing a nearest neighbor on all the intersections in the network - i.e. each variable is abstracted to exist at one of the nodes of the network.  If this is a problem-  for instance a large parcel in the city - it might be necessary to split up the object to many nearby nodes, which is an extra step but fits within the same framework.

3) perform the aggregation

The main use case of UrbanAccess is to perform an aggregation.  The api is designed to perform the aggregations for all nodes in the network at the same time in a multi-threaded fashion.  Most accessibility queries can be performed in well under a second, even for hundreds of thousands of nodes.  To perform an aggregation, pass a radius, an aggregation type (min, max, sum, mean, stddev), and a decay (flat, linear, exponential).  Decays can be applied to the variable to that items further away have less of an impact on the node for which the query is being performed.  In other words, the aggregation is performed for the whole network - in the Bay Area this is 226K nodes - and a buffer query up to the radius, typically 500 meters to about 45 minutes travel time, is performed for each node.

4) perform other queries

Because the underlying network operations are performed by the Open Source Routing Machine, "find nearest" queries are also possible as well as point-to-point travel times.

Acknowledgments
==============

None of this would be possible without the help of Dennis Luxen (now at MapBox) and his OSRM (https://github.com/DennisOSRM/Project-OSRM).

OSRM also has a dependency on Google's sparsehash project (https://code.google.com/p/sparsehash/).  

Nearest neighbor queries are performed with the fastest k-d tree around, e.g. ANN (http://www.cs.umd.edu/~mount/ANN/).  

Install
=====
All source code is included in this project with absolutely no other dependencies.  On Linux/Mac, simply run make.  Or build on Windows using the solution provided in the winaccess folder.  Once the project is built, you can install the Python wrappers to the system directory using distutils, e.g. "python setup.py install"

UPDATE: On Mac, make sure to have actual gcc (not clang).  This works for my by installing macports and then running "port install gcc49" or whatever the latest version is.

Docs
====

Docs are on the wiki (or will be soon;)

