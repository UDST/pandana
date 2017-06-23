Network API
-----------

API changes: migration notes from version 3.0 to 4.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting on version 4.0, calls to ``init_pois`` are no longer necessary due to an improvement in the
C++ backend. From that version on, the ``max_distance`` and the ``max_pois`` parameters are directly
specified by category in the :py:meth:`pandana.network.Network.set_pois` call.



.. automodule:: pandana.network
   :members:
