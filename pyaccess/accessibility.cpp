#include "accessibility.h"
# if BOOST
#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/serialization/vector.hpp>
#include <boost/serialization/utility.hpp>
#endif

namespace MTC {
	namespace accessibility {
		Accessibility::Accessibility(int _numnodes)
		{
			numnodes = _numnodes;
			dmsradius = -1;
		}
        bool Accessibility::saveCSV(std::string filename)
        {
	        std::ofstream ofs(filename);
            ofs << "impno,node1,node2,dist\n";
            for(int i = 0 ; i < dms.size() ; i++) {
                for(int j = 0 ; j < dms[i].size() ; j++) {
                    for(int k = 0 ; k < dms[i][j].size() ; k++) {
                        ofs << i << "," << j << "," << (int)dms[i][j][k].first << "," << 
                                             (float)dms[i][j][k].second << "\n";
                    }
                }
            }
        }
#if BOOST
		bool Accessibility::saveFile(std::string filename)
		{
#if DOTIMER
			QTime tazTimer;
			tazTimer.start();
			FILE_LOG(logINFO) << "START --- Saving network accessibility file.\n";
#endif
			try {
				std::ofstream ofs;
                ofs.open(filename.c_str(), ios::binary);
				boost::archive::binary_oarchive oa(ofs);
				oa << *this;
			} catch(exception &e) {
				FILE_LOG(logINFO) << "Storage::saveFile: Exception while creating network accessibility file.\n";
				return false;
			}
#if DOTIMER
			FILE_LOG(logINFO) << "END ----- Saving network accessibility serialized file: " << tazTimer.elapsed() <<" ms\n";
#endif
			return true;
		}

		bool Accessibility::loadFile(std::string filename)
		{
#if DOTIMER
			QTime tazTimer;
			tazTimer.start();
			FILE_LOG(logINFO) << "START --- Loading network accessibility serialized file.\n";
#endif
			try {
				std::ifstream ifs;
                ifs.open(filename.c_str(), ios::binary);
				boost::archive::binary_iarchive ia(ifs);
				ia >> *this;
			} catch(std::exception &e) {
				FILE_LOG(logINFO) << "Storage::loadFile: Exception while reading network accessibility file.  " << e.what() << "\n";
				return false;
			} catch(...) {
				FILE_LOG(logINFO) << "Storage::loadFile: Exception while reading network accessibility file.\n";
				return false;
			}
#if DOTIMER
			FILE_LOG(logINFO) << "END ----- Loading network accessibility serialized file: " << tazTimer.elapsed() <<" ms \n";
#endif
			return true;
		}
#endif
		double
		Accessibility::compute_street_design_var(DistanceVec &distances, 
												std::string type, float radius,
												int gno) {
#if USEBGL
			Graphalg::roadBGLGraph &graph = ga[gno]->graph;
	
			double streetlength_sum = 0.0, additionalstreetlength_sum = 0.0;
			int numedges = 0;
			int fourwayintersections_cnt = 0, culdesacs_cnt = 0, accesspoint_cnt = 0;
			double curvature_accumulator = 0.0;

			std::map<int, double> dm;
			for(int i = 0 ; i < distances.size() ; i++) {
				if(distances[i].second > radius) continue;
                dm[distances[i].first] = distances[i].second;
			}

			for(int i = 0 ; i < distances.size() ; i++) {

				int source = distances[i].first;
				double distance = distances[i].second;

				if(out_degree(source, graph) >= 4) fourwayintersections_cnt++;
				if(out_degree(source, graph) == 1) culdesacs_cnt++;

				Graphalg::roadGraphOutEdgeIter e, e_end;

				for (tie(e, e_end) = out_edges(source, graph); e != e_end; e++) {
					assert(boost::source(*e, graph) == source);

					int target = boost::target(*e,graph);

					if(dm.find(target) == dm.end()) {

						accesspoint_cnt++; 

						double additionallength_in_feet = (radius-distance) * 1000 * 3.28084;
						additionalstreetlength_sum += additionallength_in_feet;

					} else {
						if(target < source) continue; // we're going to encounter each edge twice

						double length_in_feet = 
						graph[boost::edge(source,target,graph).first].edge_weight * 1000 * 3.28084;
						streetlength_sum += length_in_feet;
						numedges++;

						float dx = graph[source].x-graph[target].x;
						float dy = graph[source].y-graph[target].y;
						double straight_line_distance = sqrt(dx*dx+dy*dy);
						straight_line_distance *= 3.28084;
						if(straight_line_distance != 0) // this is weird - I guess navteq has a couple of self-edges
						    curvature_accumulator += length_in_feet / straight_line_distance;
						else curvature_accumulator += 1.0;
					}
				}
			}

			if(type == "LINEALSTREETFEET") return streetlength_sum + additionalstreetlength_sum;

			else if(type == "AVERAGEBLOCKLENGTH") {
				if(numedges == 0) return 0;
				return streetlength_sum / (float)numedges;

			} else if(type == "NUMSTREETEDGES") {
				return numedges;

			} else if(type == "PCT4WAYINTERSECTIONS") {
				return (float)fourwayintersections_cnt / (float)distances.size();

			} else if(type == "NUMCULDESACS") {
				return culdesacs_cnt;

			} else if(type == "AVEEDGECURVATURE") {
				if(numedges == 0) return 1;
				return max(1.0,curvature_accumulator / (double)numedges);

			} else if(type == "NUMACCESSPOINTS") {
				return accesspoint_cnt;
			}

			assert(0);
#endif
			return 0;
		}

		double Accessibility::compute_centrality(
										int srcnode, DistanceVec &distances,
									    int gno) {
			if(distances.size() < 3) return 0.0;
			int cnt = 0;
			for(int i = 0 ; i < distances.size() ; i++) {
				int source = distances[i].first;
				for(int j = 0 ; j < distances.size() ; j++) {
					int target = distances[j].first;

					if(target <= source) continue;
					std::vector<NodeID> path = ga[gno]->Route(
											source,target,omp_get_thread_num());

					for(int i = 0 ; i < path.size() ; i++) {
						if(path[i] == srcnode) cnt++;
					}
				}
			}
			double n = distances.size();
			double scale = 2.0 / (n*n-3.0*n+2.0);
			return (double)cnt * scale;
		}

		double
		Accessibility::computeDesignVariable(int srcnode, float radius, std::string type, int gno) {
			
			DistanceVec distances;
			ga[gno]->Range(srcnode,radius,omp_get_thread_num(),distances);

			if(type == "CENTRALITY") {
				return compute_centrality(srcnode, distances);
			}

			else if(type == "LINEALSTREETFEET" ||
			   type == "AVERAGEBLOCKLENGTH" ||
			   type == "NUMSTREETEDGES" ||
			   type == "PCT4WAYINTERSECTIONS" ||
			   type == "NUMCULDESACS" ||
			   type == "AVEEDGECURVATURE" ||
			   type == "NUMACCESSPOINTS") {
				return compute_street_design_var(distances,type,radius);
			}
			
			if( type == "NUMNODES" ) {
				return distances.size();
			}
			
			else assert(0);

			return 0;
		}

		void Accessibility::initializePOIs(int numcategories, double maxdist, int maxitems) {
            // initialize for all subgraphs
            for(int i = 0 ; i < ga.size() ; i++) {
			    ga[i]->initPOIs(numcategories,maxdist,maxitems);
            }
			accessibilityVarsForPOIs.resize(numcategories);	
		}

		void Accessibility::initializeCategory(int category, accessibility_vars_t &vars) {
#if DOTIMER
			QTime dbTimer;
			dbTimer.start();
			FILE_LOG(logINFO) << "START --- adding points of interest\n";
#endif

			assert(vars.size() == numnodes);
			accessibilityVarsForPOIs[category] = vars;

			int cnt = 0;
			for(int i = 0 ; i < vars.size() ; i++) {
				for(int j = 0 ; j < vars[i].size() ; j++) {
					cnt++;
					for(int k = 0 ; k < ga.size() ; k++) {
					    ga[k]->addPOIToIndex(category,i);
					}
				}
			}
#if DOTIMER
			FILE_LOG(logINFO) << "END --- adding " << cnt << " points of interest in " << 
																	dbTimer.elapsed() <<" ms\n";
#endif
		}
		
		void Accessibility::initializeAccVars(int numcategories) {
			accessibilityVars.resize(numcategories);	
		}

		void Accessibility::initializeAccVar(int category, accessibility_vars_t &vars) {
			assert(vars.size() == numnodes);
			accessibilityVars[category] = vars;
		}

		std::vector<float>
		Accessibility::findNearestPOIs(int srcnode, float maxradius, int number, 												POI_category_t cat, int gno) {

			assert(cat >= 0 && cat < POI_MAXVAL);

			DistanceMap distances = ga[gno]->NearestPOI(
																	cat,srcnode,maxradius,number,
																	omp_get_thread_num());
			std::vector<float> ret;

			accessibility_vars_t &vars = accessibilityVarsForPOIs[cat];

			/* need to account for the possibility of having multiple locations at single node */
			for (DistanceMap::const_iterator itDist = distances.begin(); 
														itDist != distances.end(); ++itDist) { 
				int 	nodeid = itDist->first;
				double 	distance = itDist->second;

				for(int i = 0 ; i < vars[nodeid].size() ; i++) {

					if(vars[nodeid][i] == 0) continue;
					ret.push_back((float)distance);
					if(ret.size()==number) break;
				}
				if(ret.size()==number) break;
			}
			std::sort(ret.begin(),ret.end());
				
			return ret;
		}

		std::vector<double>
		Accessibility::findAllNearestPOIs(float maxradius, POI_category_t cat) {
			std::vector<double> dists(numnodes);
			#pragma omp parallel for
			for(int i = 0 ; i < numnodes ; i++) {
				std::vector<float> d = findNearestPOIs(i,maxradius,1,cat);
                if(d.size()) dists[i] = d[0];
                else dists[i] = -1;
			}
			return dists;
		}
		
		/*double
		Accessibility::computeEntropy(int srcnode, float radius, ENTROPY_category_t cat) {
			if( aggtyp == MTC::simulation::AGG_ENTROPY ) {
				
				assert(var_index < num_diversity_var_names);
				return entropy.computeEntropy(sum_histogram,(histogram_types_t)var_index);

			} else if ( aggtyp == MTC::simulation::AGG_HHI ) {

				assert(var_index < num_diversity_var_names);
				return entropy.HHI(sum_histogram,(histogram_types_t)var_index);

			}
			return 0;
		}*/
		
		void
		Accessibility::precomputeRangeQueries(float radius) {

			dms.resize(ga.size());
			for(int i = 0 ; i < ga.size() ; i++) {
			    dms[i].resize(numnodes);
			}

#if DOTIMER
			FILE_LOG(logINFO) << "START --- precompute distance maps, numnodes=" << numnodes << "\n";
			QTime dbTimer;
			dbTimer.start();
#endif
			#pragma omp parallel
			{
			#pragma omp for schedule(guided)
			for(int i = 0 ; i < numnodes ; i++) {
                for(int j = 0 ; j < ga.size() ; j++) {
				    ga[j]->Range(i,radius,omp_get_thread_num(),dms[j][i]);
				}
			}
			}
#if DOTIMER
			FILE_LOG(logINFO) << "END ----- precomputing distance maps in " 
											<< dbTimer.elapsed() <<" ms\n";
#endif
			
			dmsradius = radius;
		}				

		std::vector<double>
		Accessibility::getAllAggregateAccessibilityVariables(float radius, 
						int ind,
						aggregation_types_t aggtyp, decay_func_t decay,
						int graphno) {
						
			if(ind == -1) assert(0); 

			std::vector<double> scores(numnodes);
#if DOTIMER
			FILE_LOG(logINFO) << "START --- computing all aggregate vars\n";
			QTime dbTimer;
			dbTimer.start();
#endif

			#pragma omp parallel //num_threads(12)
			{
			#pragma omp for schedule(guided)
			for(int i = 0 ; i < numnodes ; i++) {
				scores[i] = aggregateAccessibilityVariable(i, radius, 
													accessibilityVars[ind],
													aggtyp, decay,
													graphno);
			}
			}
#if DOTIMER
			FILE_LOG(logINFO) << "END ----- computing all aggregate vars in " 
											<< dbTimer.elapsed() <<" ms\n";
#endif
			return scores;
		}

        DistanceVec
		Accessibility::Range(int srcnode,float radius,int gno) {
			DistanceVec tmp;
			DistanceVec &distances = tmp;
			if(dmsradius > 0 && radius <= dmsradius) {
 				distances = dms[gno][srcnode];
                return distances;
			} else {
				ga[gno]->Range(srcnode,radius,omp_get_thread_num(),tmp);
                return tmp;
			}
        }

		double
		Accessibility::aggregateAccessibilityVariable(int srcnode, float radius,
									accessibility_vars_t &vars,
									aggregation_types_t aggtyp, 
									decay_func_t decay,
									int gno) {

			assert(aggtyp >= 0 && aggtyp < AGG_MAXVAL);
			assert(decay >= 0 && decay < DECAY_MAXVAL);

			// I don't know if this is the best way to do this but I 
			// I don't want to copy memory in the precompute case - sometimes
			// I need a reference and sometimes not
			DistanceVec tmp;
			DistanceVec &distances = tmp;
			if(dmsradius > 0 && radius <= dmsradius) {
 				distances = dms[gno][srcnode];
			} else {
				ga[gno]->Range(srcnode,radius,omp_get_thread_num(),tmp);
			}

			if(distances.size() == 0) return -1;
		    if(aggtyp == AGG_STDDEV) decay = DECAY_FLAT;
        	
			int cnt = 0;
			double sum = 0.0;
			double sumsq = 0.0;

			for (int i = 0 ; i < distances.size() ; i++) { 

				int nodeid = distances[i].first;
				double distance = distances[i].second;
				
				// this can now happen since we're precomputing
				if(distance > radius) continue; 

				for(int j = 0 ; j < vars[nodeid].size() ; j++) {

					cnt++; // count items

					if(decay == DECAY_EXP) {

						sum += exp(-1*distance/radius) * vars[nodeid][j];

					} else if(decay == DECAY_LINEAR) {

						sum += (1.0-distance/radius) * vars[nodeid][j];

					} else if(decay == DECAY_FLAT) {

						sum += vars[nodeid][j];

					} else assert(0);
						
                    // stddev is always flat
                    sumsq += vars[nodeid][j]*vars[nodeid][j];
				}
			}

			if(aggtyp == AGG_COUNT) return cnt;

			if(aggtyp == AGG_AVE && cnt != 0) sum /= cnt;
			
            if(aggtyp == AGG_STDDEV && cnt != 0) { 
              double mean = sum / cnt;
              return sqrt(sumsq / cnt - mean * mean);
            }

			return sum;
		}

		std::vector<double>
		Accessibility::getAllModelResults(float radius, int numvars, int *varindexes, float *varcoeffs,
                        float distcoeff, float asc, float denom, float nestdenom, float mu, int graphno) {
						
			std::vector<double> scores(numnodes);
#if DOTIMER
			FILE_LOG(logINFO) << "START --- computing all model results\n";
			QTime dbTimer;
			dbTimer.start();
#endif

			#pragma omp parallel //num_threads(12)
			{
			#pragma omp for schedule(guided)
			for(int i = 0 ; i < numnodes ; i++) {
                double utility = 0.0;
				scores[i] = modelResult(i, radius, numvars, varindexes, varcoeffs,
                        distcoeff, asc, denom, nestdenom, mu, graphno);
			}
			}
#if DOTIMER
			FILE_LOG(logINFO) << "END ----- computing all model results in " 
											<< dbTimer.elapsed() <<" ms\n";
#endif
			return scores;
		}

		double
		Accessibility::modelResult(int srcnode, float radius, int numvars, int *varindexes, float *varcoeffs,
                        float distcoeff, float asc, float denom, float nestdenom, float mu, int gno) {

			// I don't know if this is the best way to do this but I 
			// I don't want to copy memory in the precompute case - sometimes
			// I need a reference and sometimes not
			DistanceVec tmp;
			DistanceVec &distances = tmp;
			if(dmsradius > 0 && radius <= dmsradius) {
 				distances = dms[gno][srcnode];
			} else {
				ga[gno]->Range(srcnode,radius,omp_get_thread_num(),tmp);
			}

			if(distances.size() == 0) return -1;
			
			double sum = 0.0;

			for (int i = 0 ; i < distances.size() ; i++) { 

				int nodeid = distances[i].first;
				double distance = distances[i].second;
                double utility = 0.0;
				
				// this can now happen since we're precomputing
				if(distance > radius) continue; 

                utility += asc;
                utility += distance * distcoeff;

                for(int j = 0 ; j < numvars ; j++) {

					accessibility_vars_t &vars = accessibilityVars[varindexes[j]];

				    for(int k = 0 ; k < vars[nodeid].size() ; k++) {

						utility += vars[nodeid][k] * varcoeffs[j];
					}
				}
                sum += exp(mu*utility);
			}

			return log(sum);
		}

		inline double 
		walkscore_contribution(std::vector<float> &distances, int index, 
															double weight) {
			if(index-1 >= distances.size()) return 0.0;

			// XXX this should probably be sigmoid
			// there's a factor below for conversion to miles
			double ww = -atan((distances[index-1]*.6-1)/1.3)+.5;

			if(ww > 1.0) ww = 1.0;
			if(ww < 0.0) ww = 0.0;

			return ww*weight;
		}

		std::vector<double>
		Accessibility::getAllOpenWalkscores() {

			std::vector<double> walkscores(numnodes);
#if DOTIMER
			FILE_LOG(logINFO) << "START --- computing all openwalkscores\n";
			QTime dbTimer;
			dbTimer.start();
#endif

			#pragma omp parallel //num_threads(1)
			{
			#pragma omp for schedule(guided)
			for(int i = 0 ; i < numnodes ; i++) {
				walkscores[i] = getOpenWalkscore(i);	
			}
			}
#if DOTIMER
			FILE_LOG(logINFO) << "END ----- computing all openwalkscores in " 
											<< dbTimer.elapsed() <<" ms\n";
#endif
			return walkscores;
		}

		double
		Accessibility::getOpenWalkscore(int srcnode) {
			double sum = 0.0;
			std::vector<float> distances;

			distances = findNearestPOIs(srcnode,2.4,1,POI_GROCERY); 
			sum += walkscore_contribution(distances,1,3.0);

			distances = findNearestPOIs(srcnode,2.4,10,POI_RESTAURANTS); 
			sum += walkscore_contribution(distances,1,.75);
			sum += walkscore_contribution(distances,2,.45);
			sum += walkscore_contribution(distances,3,.25);
			sum += walkscore_contribution(distances,4,.25);
			sum += walkscore_contribution(distances,5,.225);
			sum += walkscore_contribution(distances,6,.225);
			sum += walkscore_contribution(distances,7,.225);
			sum += walkscore_contribution(distances,8,.225);
			sum += walkscore_contribution(distances,9,.2);
			sum += walkscore_contribution(distances,10,.2);

			distances = findNearestPOIs(srcnode,2.4,5,POI_SHOPPING); 
			sum += walkscore_contribution(distances,1,.5);
			sum += walkscore_contribution(distances,2,.45);
			sum += walkscore_contribution(distances,3,.4);
			sum += walkscore_contribution(distances,4,.35);
			sum += walkscore_contribution(distances,5,.3);

			distances = findNearestPOIs(srcnode,2.4,2,POI_COFFEESHOPS); 
			sum += walkscore_contribution(distances,1,1.25);
			sum += walkscore_contribution(distances,2,.75);
			
			distances = findNearestPOIs(srcnode,2.4,1,POI_BANKS); 
			sum += walkscore_contribution(distances,1,1.0);

			distances = findNearestPOIs(srcnode,2.4,1,POI_PARKS); 
			sum += walkscore_contribution(distances,1,1.0);

			distances = findNearestPOIs(srcnode,2.4,1,POI_SCHOOLS); 
			sum += walkscore_contribution(distances,1,1.0);

			distances = findNearestPOIs(srcnode,2.4,1,POI_BOOKSTORES); 
			sum += walkscore_contribution(distances,1,1.0);
			
			distances = findNearestPOIs(srcnode,2.4,1,POI_ENTERTAINMENT); 
			sum += walkscore_contribution(distances,1,1.0);
			
			sum *= 6.67;
			
			// XXX need to add penalty for design variables

			return sum;
		}
	}	
}
