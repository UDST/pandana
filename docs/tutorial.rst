Tutorial
--------

At this point it is probably helpful to make concrete the topics discussed in
the introduction by giving code sample.  There is also an IPython Notebook
in the ``Pandana`` repo which gives the entire workflow,
but the discussion here will take things line-by-line with a sufficient
summary of the functionality.

Note that these code samples assume you have imported pandana as follows::

    import pandana as pdna

Create the Network
~~~~~~~~~~~~~~~~~~

First create the network.  Although the API is incredibly simple,
this is likely to be the most difficult part of using Pandana.  In the future
we will leverage the import functionality of tools like ``geopandas`` to
directly access OpenStreetMap and networks via shapefiles,
but for now the initialization :py:meth:`pandana.network.Network.__init__`
takes a small number of Pandas Series objects.

The network is comprised of a set of nodes and edges.  We store our nodes and
edges as two Pandas DataFrames in an HDFStore object.  We can access them as
follows: ::


    store = pd.HDFStore('data/osm_bayarea.h5', "r")
    nodes = store.nodes
    edges = store.edges
    print nodes.head(3)
    print edges.head(3)


The output of the above code shows: ::


                  x           y
    8   629310.1250  4095536.75
    9   629120.9375  4095816.75
    10  628951.5625  4096090.50

    [3 rows x 2 columns]

       from  to      weight
    6     8   9  338.255005
    7     9  10  322.532990
    8    10  11  218.505997

    [3 rows x 3 columns]


The data structure is very simple indeed.  Nodes have an index which is the
id of the node and an x-y position.  Much like ``shapely``, ``Pandana`` is
agnostic to the  coordinate system.  Use your local coordinate system or
longitude then latitude - either one will work.  Edges are then ids (which
aren't used) and
``from`` node ids and ``to`` node_ids which should index directly to the node
DataFrame.  A ``weight`` column (or multiple weight columns) is (are) required
as the impedance for the network.  Here distance is used from OpenStreetMap
edges.

To create the network given the above DataFrames, simply call: ::


    net=pdna.Network(nodes["x"], nodes["y"], edges["from"], edges["to"],
                     edges[["weight"]])

It's probably a good idea (though not strictly required) to precompute a
given horizon distance so that aggregations don't perform the network queries
unnecessarily.  This is done by calling the following code,
where 3000 meters is used as the horizon distance: ::

    net.precompute(3000)

Note that a large amount of time is spent in the precomputations that take
place for these two lines of code.  On my MacBook, these two lines of code
take 4 seconds and 8.5 seconds respectively.

**I also have a 4-core cpu, so if your precomputation is much slower,
check the IPython Notebook output (on the console) for a statement that says**
``Generating contraction hierarchies with 4 threads.`` **If your output says
1 instead of 4 you are running single threaded.  If you are running on
a multi-core cpu, there is probably a way to speed up the computation.**

Assign variables and perform computations for nearest queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now for the fun part.  Nearest queries are slightly easier, so let's cover that
first.

First initialize the POI (point-of-interest) engine.  This is a bit
strange for Python programmers, but because this code wraps a C++ API,
you need to initialize the memory first.  This is not a strict requirement
though, and future versions might remedy this. ::

    net.init_pois(num_categories=1, max_dist=2000, max_pois=10)

This initializes one category, at a max distance of 2000 meters for up to the
10 nearest points-of-interest.

Here is a link to the docs: :py:meth:`pandana.network.Network.init_pois`

Next initialize the category: ::

    net.set_pois("restaurants", x, y)

This code initializes the "restaurants" category with the positions specified
by the x and y columns (which are Pandas Series).  Next perform the query:

Here is a link to the docs: :py:meth:`pandana.network.Network.set_pois` ::

    net.nearest_pois(2000, "restaurants", num_pois=10)

This searches for the 10 nearest restaurants and is exactly the query that is
displayed in the introduction.  This returns a DataFrame with the number of
columns equal to the number of POIs that are requested. For instance,
a describe of the output DataFrame look like this (note that the query
executed in half a second: ::

    CPU times: user 1.37 s, sys: 11 ms, total: 1.38 s
    Wall time: 498 ms
                      1              2              3              4   \
    count  226060.000000  226060.000000  226060.000000  226060.000000
    mean     1542.487481    1676.578324    1746.392002    1794.982571
    std       629.581983     543.853257     485.754919     440.356407
    min         0.000000       0.000000       0.000000       0.000000
    25%      1063.236542    1473.924011    1775.853271    2000.000000
    50%      2000.000000    2000.000000    2000.000000    2000.000000
    75%      2000.000000    2000.000000    2000.000000    2000.000000
    max      2000.000000    2000.000000    2000.000000    2000.000000

                      5              6              7              8   \
    count  226060.000000  226060.000000  226060.000000  226060.000000
    mean     1825.214545    1846.061683    1864.423958    1879.123914
    std       407.388660     380.878320     353.350067     330.835422
    min         0.000000       0.000000       0.000000       0.000000
    25%      2000.000000    2000.000000    2000.000000    2000.000000
    50%      2000.000000    2000.000000    2000.000000    2000.000000
    75%      2000.000000    2000.000000    2000.000000    2000.000000
    max      2000.000000    2000.000000    2000.000000    2000.000000

                      9              10
    count  226060.000000  226060.000000
    mean     1893.909935    1908.403787
    std       306.340819     283.554353
    min         0.000000      56.143002
    25%      2000.000000    2000.000000
    50%      2000.000000    2000.000000
    75%      2000.000000    2000.000000
    max      2000.000000    2000.000000

    [8 rows x 10 columns]

Here is a link to the docs: :py:meth:`pandana.network.Network.nearest_pois`

Assign variables and perform computations for aggregation queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display the results
~~~~~~~~~~~~~~~~~~~
