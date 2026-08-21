# Pandana project history

Pandana was developed at the University of California, Berkeley, as part of a research program led by Paul Waddell on parcel-scale land-use, transportation, and accessibility modeling.

## Origins

The collaboration grew from a seminar Waddell presented to the algorithm-engineering research group at the Karlsruhe Institute of Technology. There he met Dennis Luxen, whose work on contraction hierarchies and the Open Source Routing Machine provided a high-performance foundation for regional network analysis. Waddell subsequently recruited and funded Luxen to work with the Berkeley team for a limited period.

Waddell, Fletcher Foti, and Luxen jointly conceptualized an application that would connect parcel-level land-use information with complete street networks, including local streets and pedestrian-scale access. Foti was Waddell's doctoral student and graduate student researcher at Berkeley and led implementation of the initial Pandana software. Waddell provided research direction, supervision, and project funding. Luxen contributed routing expertise and contraction-hierarchy code.

Initial development was supported in part by National Science Foundation award [IIS-0964412, *Integrating Behavioral, Geometrical and Graphical Modeling to Simulate and Visualize Urban Areas*](https://www.nsf.gov/awardsearch/showAward?AWD_ID=0964412). Waddell was principal investigator for the UC Berkeley component, with Michael Jordan as co-principal investigator; the collaborative project included Daniel Aliaga and Bedrich Benes at Purdue University. The work also received support from the Metropolitan Transportation Commission through its UrbanSim visualization and sustainable-communities research program, led at Berkeley by Waddell with Aliaga as co-principal investigator.

Foti, Waddell, and Luxen described the original framework in their 2012 paper, [*A Generalized Computational Framework for Accessibility: From the Pedestrian to the Metropolitan Scale*](https://onlinepubs.trb.org/onlinepubs/conferences/2012/4thITM/Papers-A/0117-000062.pdf). The paper presented a unified graph linking parcels and complete street networks and reported regional-scale accessibility performance using contraction hierarchies.

## Subsequent development

Pandana became part of the Urban Data Science Toolkit and was extended by Matt Davis, Federico Fernandez, Sam Maurer, and other contributors. Later releases added updated Python support, plotting and installation improvements, vectorized and multithreaded shortest-path methods, range queries, point-of-interest enhancements, and modern packaging.

After a period of limited maintenance, community work kept Pandana usable with newer scientific Python releases. Eli Knaap opened the initial NumPy 2 compatibility work in pull request #196 and subsequently led development of the Pandarm friendly fork with other contributors. Joaquim Gromicho expanded and completed the Pandana modernization in pull request #198, including current Python and NumPy compatibility, legacy HDF handling, regression tests, and cross-platform wheel infrastructure. Work adapted from #196 is credited in the changelog and integration history.

## Attribution

Project history includes several distinct forms of contribution: conception and research leadership, grant and agency support, software implementation, routing algorithms, maintenance, testing, packaging, documentation, and downstream application. This account records the origins and institutional context of Pandana without replacing the more detailed authorship record in Git commits, pull requests, releases, and publications.

