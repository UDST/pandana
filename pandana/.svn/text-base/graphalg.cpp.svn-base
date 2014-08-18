#include "graphalg.h"
#include <math.h>
#include "omp.h"

namespace MTC {
	namespace accessibility {

		void Graphalg::BuildNN(std::vector<float> x, std::vector<float> y) {
			assert(x.size() == y.size());
			int numnodes = x.size();
			nearestNeighbor.Expand(numnodes);
			for(int i = 0 ; i < numnodes ; i++)
			{
				nearestNeighbor.setPoint(i,x[i],y[i]);
			}			
			nearestNeighbor.buildTree();
		}

		void Graphalg::Build(int *nodeids, float *nodesxy, int numnodes,
							int *edges, float *edgeweights, int numedges,
							bool twoway) {

			this->numnodes = numnodes;
			this->usech = USECH;
#if USEBGL
			for(int i = 0 ; i < numedges ; i++) {
				int srcVertex = edges[i*2+0];
				int tgtVertex = edges[i*2+1];
				std::pair<edge_descriptor, bool> tmp_pair
					= boost::add_edge(srcVertex, tgtVertex, graph);
				graph[tmp_pair.first].edge_weight = edgeweights[i];
			}
			for(int i = 0 ; i < numnodes ; i++) {
				graph[i].x = nodesxy[i*2+0];
				graph[i].y = nodesxy[i*2+1];
			}
#endif
			int num = 12; //omp_get_max_threads();
			FILE_LOG(logINFO) << "Generating contraction hierarchies with " << num << " threads.\n";
			ch = CH::ContractionHierarchies(num);

			vector<CH::Node> nv;

			for(int i = 0 ; i < numnodes ; i++)
			{
				CH::Node n(nodeids[i],nodesxy[i*2+0],nodesxy[i*2+1]);
				nv.push_back(n);
			}
			FILE_LOG(logINFO) << "Setting CH node vector of size " << nv.size() << "\n";

			ch.SetNodeVector(nv);

			vector<CH::Edge> ev;

			for(int i = 0 ; i < numedges ; i++) {

				CH::Edge e(edges[i*2+0],edges[i*2+1],i,
								edgeweights[i]*DISTANCEMULTFACT, true, twoway); 
				ev.push_back(e);
			}

			FILE_LOG(logINFO) << "Setting CH edge vector of size " << ev.size() << "\n";
			ch.SetEdgeVector(ev);
#if DOTIMER
			QTime dbTimer;
			dbTimer.start();
			FILE_LOG(logINFO) << "START -- Creating contraction hierarchies.\n";
#endif

			ch.RunPreprocessing();
#if DOTIMER
			FILE_LOG(logINFO) << "END ----- Creating contraction hierarchies " << 
																	dbTimer.elapsed() <<" ms \n";
#endif

			nearestNeighbor.Expand(numnodes);
			for(int i = 0 ; i < numnodes ; i++)
			{
				nearestNeighbor.setPoint(i,nodesxy[i*2+0],nodesxy[i*2+1]);
			}
#if DOTIMER
			dbTimer.start();			
#endif
			nearestNeighbor.buildTree();
#if DOTIMER
			FILE_LOG(logINFO) << "Built quad tree in " << dbTimer.elapsed() <<" ms\n";
#endif
		}

		int Graphalg::NearestNode(float x, float y, double *distance) {
			int *indexes;
			double *distances;
			nearestNeighbor.Query(x,y,1,-1,&indexes,&distances);
			int i = indexes[0];
            if(distance) *distance = distances[0];	
			delete []indexes;
			delete []distances;
			return i;
		}

		std::vector<NodeID> Graphalg::Route(int src, int tgt, int threadNum) {

			std::vector<NodeID> ResultingPath;

			CH::Node src_node(src,0,0);
			CH::Node tgt_node(tgt,0,0);
			
			ch.computeShortestPath(src_node,tgt_node,ResultingPath,threadNum);

			return ResultingPath;
		}

		double Graphalg::Distance(int src, int tgt, int threadNum) {

			CH::Node src_node(src,0,0);
			CH::Node tgt_node(tgt,0,0);
			
			unsigned int length = ch.computeLengthofShortestPath(src_node,tgt_node,threadNum);

			return (double)length/(double)DISTANCEMULTFACT;
		}

		void Graphalg::Range(int src, double maxdist, int threadNum, 
												DistanceVec &ResultingNodes) {

			CH::Node src_node(src,0,0);

		    std::vector<std::pair<NodeID, unsigned> > tmp;

			ch.computeReachableNodesWithin(src_node, 
									maxdist*DISTANCEMULTFACT,tmp,
									threadNum);

			for(int i = 0 ; i < tmp.size() ; i++) {
				std::pair<NodeID, float> node;
				node.first = tmp[i].first;
				node.second = tmp[i].second/DISTANCEMULTFACT;
				ResultingNodes.push_back(node);
			}
		}
		
		DistanceMap
		Graphalg::NearestPOI(int category, int src, double maxdist, int number,
																				int threadNum) {
			DistanceMap dm;

			std::vector<CH::BucketEntry> ResultingNodes;
			ch.getNearestWithUpperBoundOnDistanceAndLocations(category,src,
													maxdist*DISTANCEMULTFACT,number,ResultingNodes,
													threadNum);

			for(int i = 0 ; i < ResultingNodes.size() ; i++) {
				dm[ResultingNodes[i].node] = 
									((float)ResultingNodes[i].distance)/(float)DISTANCEMULTFACT;
			}

			return dm;

		}
	}
}
