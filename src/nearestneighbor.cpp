#include "nearestneighbor.h"
#include <assert.h>

namespace MTC {
	namespace accessibility {
		NearestNeighbor::NearestNeighbor(int nPts)
		{
			this->nPts = nPts;
			try {
				dataPts = annAllocPts(nPts, dim);	// allocate data points
			}
			catch (const std::bad_alloc& e) {
				FILE_LOG(logINFO)
				       << "Bad Allocation in Nearest Neighbor - annAllocPts("
					   << nPts << ")";
			}
		}

		NearestNeighbor::~NearestNeighbor(void)
		{
			//annClose();			
		}

		void NearestNeighbor::Expand(int nPts) {
			this->nPts = nPts;
			dataPts = annAllocPts(nPts, dim);	  // allocate data points
		}

		void NearestNeighbor::setPoint(int ind, double x, double y) {
			dataPts[ind][0] = x;
			dataPts[ind][1] = y;
		}

		void NearestNeighbor::buildTree() {
			assert(nPts >= 0);
 			kdTree = new ANNkd_tree(			// build search structure
					dataPts,					// the data points
					nPts,						// number of points
					dim); 						// dimension of space
		}

		void
		NearestNeighbor::dump() {
			/*std::ofstream myfile;
			myfile.open ("kdtree.out");
			kdTree[0]->Dump(ANNtrue,myfile);
			myfile.close();*/
		}

		/* this does the nearest neighbor search and returns an array of length
		   numberofneighbors in both the retpIndexes and retpDistance output
		   arrays.  If there was not a neighbor in a certain slot,
		   retpIndexes[i] will equal -1 WARNING! Delete the output memory
		   arrays */

		int NearestNeighbor::Query(double x, double y, int numberofneighbors,
		          double distance, int **retpIndexes, double **retpDistances) {
			ANNpoint			queryPt;	// query point
			ANNidxArray			nnIdx;		// near neighbor indices
			ANNdistArray		dists;		// near neighbor distances

			double				eps = 0.0;
			int					k = numberofneighbors;

			queryPt = annAllocPt(dim);		// allocate query point
			queryPt[0] = x;
			queryPt[1] = y;

			nnIdx = new ANNidx[k];			// allocate near neigh indices
			dists = new ANNdist[k];			// allocate near neighbor dists

			assert(k>0);
			assert(distance == -1 || distance < 500);

			if(distance == -1) {
				kdTree->annkSearch(			// search
					queryPt,				// query point
					k,						// number of near neighbors
					nnIdx,					// nearest neighbors (returned)
					dists,					// distance (returned)
					eps);					// error bound
			} else {
				kdTree->annkFRSearch(		// search
					queryPt,				// query point
					distance*distance,		// max distance radius
					k,						// number of near neighbors
					nnIdx,					// nearest neighbors (returned)
					dists,					// distance (returned)
					eps);					// error bound
			}

			for(int i = 0 ; i < k ; i++) {
				assert(dists[i] >= 0);
				assert(i<k); 				// for ilke's bug
				dists[i] = sqrt(dists[i]);	// unsquare distance
			}

			*retpIndexes = nnIdx;
			*retpDistances = dists;

			return 0;
		}


	}
}
