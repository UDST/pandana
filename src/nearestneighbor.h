#pragma once

#include "shared.h"
#include <iostream>
#include <fstream>
#include <ANN/ANN.h>

namespace MTC {
	namespace accessibility {
		#ifdef _WIN32
			class DLLExport NearestNeighbor
		#else
			class NearestNeighbor
		#endif
		{
		public:

			NearestNeighbor(int nPts=0);
			~NearestNeighbor(void);
			void Expand(int nPts);
			void setPoint(int ind, double x, double y);
			void buildTree();
			void dump();
			int Query(double x,
			          double y,
			          int numberofneighbors,
			          double distance,
					  int **retpIndexes,
					  double **retpDistances);

			ANNpointArray		dataPts;
			int					nPts;
			ANNkd_tree			*kdTree;		// search structure
			static const int	dim	= 2;		// dimension
		};
	}
}
