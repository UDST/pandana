Loaders
=======

Pandana has some support for creating a
:py:class:`~pandana.network.Network` from
the `OpenStreetMap <http://www.openstreetmap.org/>`__ API,
and for storing ``Network`` data to disk as HDF5 so that it can be
restored later.

OpenStreetMap
-------------

A :py:class:`~pandana.network.Network` is created from OpenStreetMap using
the :py:func:`~pandana.loaders.osm.pdna_network_from_bbox` function::

    from pandana.loaders import osm
    network = osm.pdna_network_from_bbox(37.859, -122.282, 37.881, -122.252)

By default the generated network contains only walkable routes,
specify ``type='drive'`` to get driveable routes.
These networks have one impedance set, named ``'distance'``,
which is the distance between nodes in meters.

.. note::
   `pdna_network_from_bbox` uses the UDST library OSMnet to download and
   process OpenStreetMap (OSM) street network data. Please see
   the `OSMnet`_ repo for any OSM loader questions, bugs, or features.

The OSM API also includes the :py:func:`~pandana.loaders.osm.node_query`
function for getting specific nodes within a bounding box.
This can be used to populate a network with points of interest::

    nodes = osm.node_query(
        37.859, -122.282, 37.881, -122.252, tags='"amenity"="restaurant"')
    network.set_pois('restaurants', 2000, 10, nodes['lon'], nodes['lat'])

For more about tags see the
`Overpass API Language Guide <http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide>`__
and the list of
`OSM map features <http://wiki.openstreetmap.org/wiki/Map_Features>`__.

Pandas HDF5
-----------

Saving a ``Network`` to HDF5 is a way to share a ``Network`` or to preserve
it between sessions. For example. you can build a ``Network`` using the
OpenStreetMap API, then save the ``Network`` to HDF5 so you can reuse it
without querying OSM again.
Users will typically use the
:py:meth:`~pandana.network.Network.save_hdf5` and
:py:meth:`~pandana.network.Network.from_hdf5` methods.

.. note::
   Only the nodes and edges of the network are saved.
   Points-of-interest and data attached to nodes via the
   :py:meth:`~pandana.network.Network.set` method are not included.

   You may find the
   `Pandas HDFStore <http://pandas.pydata.org/pandas-docs/stable/io.html#io-hdf5>`__
   useful to save POI and other data.

When saving a ``Network`` to HDF5 it's possible to exclude certain nodes.
This can be useful when refining a network so that it includes only
validated nodes.
(In the current design of Pandana it's not possible to modify a
``Network`` in place.)
As an example, you can use the
:py:meth:`~pandana.network.Network.low_connectivity_nodes` method
to identify nodes that may not be connected to the larger network,
then exclude those nodes when saving to HDF5::

    lcn = network.low_connectivity_nodes(10000, 10, imp_name='distance')
    network.save_hdf5('mynetwork.h5', rm_nodes=lcn)

OpenStreetMap API
-----------------

.. autofunction:: pandana.loaders.osm.pdna_network_from_bbox

.. autofunction:: pandana.loaders.osm.node_query

Pandas HDF5 API
---------------

.. automethod:: pandana.network.Network.save_hdf5
   :noindex:

.. automethod:: pandana.network.Network.from_hdf5
   :noindex:

.. autofunction:: pandana.loaders.pandash5.network_to_pandas_hdf5

.. autofunction:: pandana.loaders.pandash5.network_from_pandas_hdf5

.. _OSMnet: https://github.com/udst/osmnet
