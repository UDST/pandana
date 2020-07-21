Network API
-----------

API
~~~

.. automodule:: pandana.network
   :members:

Deprecations in v0.4
~~~~~~~~~~~~~~~~~~~~

Beginning with Pandana v0.4, calls to ``init_pois`` are no longer necessary due to an improvement in the
C++ backend. From that version on, the ``max_distance`` and the ``max_pois`` parameters are directly
specified by category in the :py:meth:`pandana.network.Network.set_pois` call.

The ``reserve_num_graphs`` call is also no longer required.  Pandana Network objects can now be created and destroyed on-the-fly and no initialization need be done in advance.
