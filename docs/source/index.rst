.. pandana documentation master file, created by
   sphinx-quickstart on Mon Aug 18 15:50:17 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pandana
=======

Pandana is a Python library for network analysis that uses `contraction hierarchies <https://en.wikipedia.org/wiki/Contraction_hierarchies>`_ to calculate super-fast travel accessibility metrics and shortest paths. The numerical code is in C++.

v0.8rc1, released August 21, 2026 (release candidate).


Origins and acknowledgments
---------------------------

Pandana originated in research led by Paul Waddell at the University of California, Berkeley. Waddell conceived the network-accessibility application with Fletcher Foti, then his doctoral student and graduate student researcher, and Dennis Luxen of the Karlsruhe Institute of Technology, and directed and funded the initial development.

Foti led implementation of the original software and its pandas-oriented interface. Luxen contributed contraction-hierarchy expertise and code developed through the `Open Source Routing Machine project <https://github.com/DennisOSRM/Project-OSRM>`_. Initial development was supported in part by National Science Foundation award `IIS-0964412 <https://www.nsf.gov/awardsearch/showAward?AWD_ID=0964412>`_ and by the Metropolitan Transportation Commission.

Subsequent development has included major contributions from Matt Davis, Federico Fernandez, Sam Maurer, Joaquim Gromicho, Eli Knaap, and other community contributors. The repository's ``HISTORY.md`` file provides additional context, while the Git history remains the authoritative record of individual code contributions.

A `paper on Pandana <http://onlinepubs.trb.org/onlinepubs/conferences/2012/4thITM/Papers-A/0117-000062.pdf>`_
was presented at the Transportation Research Board Annual Conference in 2012. Please cite this paper when referring to the methodology implemented by this library.


Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   introduction
   tutorial
   network
   loaders
   utilities
   changelog
   futurework

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
