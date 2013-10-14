#pragma once

#include "shared.h"
#include <vector>
#if USECH
#include <QVector3D>
#endif
#include "nearestneighbor.h"

#define USEBGL 0
#define USECH 1
#if USECH
#include "contraction_hierarchies/src/libch.h"
#endif
#if USEBGL
#include <boost/graph/adjacency_list.hpp>
#endif

typedef unsigned int NodeID;

#define DISTANCEMULTFACT 1000.0

namespace MTC {
	namespace accessibility {

		typedef std::map<int,float> DistanceMap;
		typedef std::vector<std::pair<NodeID, float> > DistanceVec;
		
		class Graphalg
		{
		public:
#if USEBGL
			class RoadGraphVertex {
				public:
				//QVector3D pt;
                float x, y;
			};
			class RoadGraphEdge {
				public:
				float edge_weight;
			};
            typedef boost::adjacency_list
                <boost::vecS, boost::vecS, boost::undirectedS, RoadGraphVertex, RoadGraphEdge> roadBGLGraph;
			typedef boost::graph_traits < roadBGLGraph >::vertex_descriptor vertex_descriptor;
			typedef boost::graph_traits < roadBGLGraph >::edge_descriptor edge_descriptor;
			typedef boost::graph_traits<roadBGLGraph>::vertex_iterator roadGraphVertexIter;
			typedef boost::graph_traits<roadBGLGraph>::edge_iterator roadGraphEdgeIter;
			typedef boost::graph_traits<roadBGLGraph>::out_edge_iterator roadGraphOutEdgeIter;

			roadBGLGraph graph;
#endif
		    void DLLExport Build(int *nodeids, float *nodexy, int numnodes,
							int *edges, float *edgeweights, int numedges,
							bool twoway);

			void DLLExport BuildNN(std::vector<float> x, std::vector<float> y);
#if USEBGL
			void Build(roadBGLGraph *graph, int num=-1);
#endif
			
			int DLLExport NearestNode(float x, float y, double *distance);

			std::vector<NodeID> Route(int src, int tgt, int threadNum=0);
		    double Distance(int src, int tgt, int threadNum=0);

			void Range(int src, double maxdist, int threadNum, 
					DistanceVec &ResultingNodes);

			DistanceMap NearestPOI(int category, int src, double maxdist, 
												int number, int threadNum=0);

			void initPOIs(int numcategories, double maxdist, int maxitems) {
#if USECH
				ch.createPOIIndexArray(numcategories,maxdist*DISTANCEMULTFACT,
															maxitems);
#else
				assert(0);
#endif
			}
			void addPOIToIndex(int category, int i) {
#if USECH
				ch.addPOIToIndex(category,i);
#else
				assert(0);
#endif
			}

			int usech;
			int numnodes;
#if USECH
			CH::ContractionHierarchies ch;
#endif
			NearestNeighbor nearestNeighbor;
		};
	}
}
