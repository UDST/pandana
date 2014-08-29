#pragma once

#include "shared.h"
#include <vector>
#include "nearestneighbor.h"
#include "contraction_hierarchies/src/libch.h"

typedef unsigned int NodeID;

#define DISTANCEMULTFACT 1000.0

namespace MTC {
	namespace accessibility {

		typedef std::map<int,float> DistanceMap;
		typedef std::vector<std::pair<NodeID, float> > DistanceVec;
		
		class Graphalg
		{
		public:

		    void DLLExport Build(int *nodeids, float *nodexy, int numnodes,
							int *edges, float *edgeweights, int numedges,
							bool twoway);

			void DLLExport BuildNN(std::vector<float> x, std::vector<float> y);
			
			int DLLExport NearestNode(float x, float y, double *distance);

			std::vector<NodeID> Route(int src, int tgt, int threadNum=0);
		    double Distance(int src, int tgt, int threadNum=0);

			void Range(int src, double maxdist, int threadNum, 
					DistanceVec &ResultingNodes);

			DistanceMap NearestPOI(int category, int src, double maxdist, 
												int number, int threadNum=0);

			void initPOIs(int numcategories, double maxdist, int maxitems) {
				ch.createPOIIndexArray(numcategories, maxdist*DISTANCEMULTFACT,
									   maxitems);
			}
			void addPOIToIndex(int category, int i) {
				ch.addPOIToIndex(category,i);
			}

			int numnodes;

			CH::ContractionHierarchies ch;
			NearestNeighbor nearestNeighbor;
		};
	}
}
