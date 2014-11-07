#include "accessibility.h"

namespace MTC {
	namespace accessibility {
		Accessibility::Accessibility(int _numnodes)
		{
			numnodes = _numnodes;
			dmsradius = -1;
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

		void Accessibility::initializePOIs(int numcategories, double maxdist,
		                                   int maxitems) {
            // initialize for all subgraphs
            for(int i = 0 ; i < ga.size() ; i++) {
			    ga[i]->initPOIs(numcategories, maxdist, maxitems);
            }
			accessibilityVarsForPOIs.resize(numcategories);
		}

		void Accessibility::initializeCategory(int category,
		                                       accessibility_vars_t &vars) {

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
		}

		void Accessibility::initializeAccVars(int numcategories) {
			accessibilityVars.resize(numcategories);
		}

		void Accessibility::initializeAccVar(int category,
		                                     accessibility_vars_t &vars) {
			assert(vars.size() == numnodes);
			accessibilityVars[category] = vars;
		}

		std::vector<float>
		Accessibility::findNearestPOIs(int srcnode, float maxradius,
		    unsigned number, unsigned cat, int gno) {

			assert(cat >= 0 && cat < POI_MAXVAL);

			DistanceMap distances = ga[gno]->NearestPOI(cat,srcnode,maxradius,
			                                            number,
														omp_get_thread_num());
			std::vector<float> ret;

			accessibility_vars_t &vars = accessibilityVarsForPOIs[cat];

			/* need to account for the possibility of having
			   multiple locations at single node */
			for (DistanceMap::const_iterator itDist = distances.begin();
				 itDist != distances.end(); ++itDist) {

				int 	nodeid = itDist->first;
				double 	distance = itDist->second;

				for(int i = 0 ; i < vars[nodeid].size() ; i++) {

					if(vars[nodeid][i] == 0) continue;
					ret.push_back((float)distance);
				}
			}
			std::sort(ret.begin(),ret.end());

			return ret;
		}

		std::vector<std::vector<float> >
		Accessibility::findAllNearestPOIs(float maxradius,
		    unsigned number, unsigned cat, int gno) {
			std::vector<std::vector<float> > dists(numnodes,
			            std::vector<float> ( number ));
			#pragma omp parallel for
			for(int i = 0 ; i < numnodes ; i++) {
				std::vector<float> d = findNearestPOIs(i, maxradius, number,
				                                       cat, gno);
				for(int j = 0 ; j < number ; j++) {
                    if(j < d.size()) dists[i][j] = d[j];
                    else dists[i][j] = -1;
                }
			}
			return dists;
		}

		void
		Accessibility::precomputeRangeQueries(float radius) {
			dms.resize(ga.size());
			for(int i = 0 ; i < ga.size() ; i++) {
			    dms[i].resize(numnodes);
			}

			#pragma omp parallel
			{
			#pragma omp for schedule(guided)
			for(int i = 0 ; i < numnodes ; i++) {
                for(int j = 0 ; j < ga.size() ; j++) {
				    ga[j]->Range(i,radius,omp_get_thread_num(),dms[j][i]);
				}
			}
			}
			dmsradius = radius;
		}

		std::vector<double>
		Accessibility::getAllAggregateAccessibilityVariables(float radius,
						int ind,
						aggregation_types_t aggtyp, decay_func_t decay,
						int graphno) {

			if(ind == -1) assert(0);

			std::vector<double> scores(numnodes);

			#pragma omp parallel
			{
			#pragma omp for schedule(guided)
			for(int i = 0 ; i < numnodes ; i++) {
				scores[i] = aggregateAccessibilityVariable(i, radius,
													accessibilityVars[ind],
													aggtyp, decay,
													graphno);
			}
			}
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
		Accessibility::getAllModelResults(float radius, int numvars,
		    int *varindexes, float *varcoeffs, float distcoeff, float asc,
		    float denom, float nestdenom, float mu, int graphno) {

			std::vector<double> scores(numnodes);

			#pragma omp parallel
			{
			#pragma omp for schedule(guided)
			for(int i = 0 ; i < numnodes ; i++) {
                double utility = 0.0;
				scores[i] = modelResult(i, radius, numvars, varindexes,
				    varcoeffs, distcoeff, asc, denom, nestdenom, mu, graphno);
			}
			}
			return scores;
		}

		double
		Accessibility::modelResult(int srcnode, float radius, int numvars,
		    int *varindexes, float *varcoeffs, float distcoeff, float asc,
		    float denom, float nestdenom, float mu, int gno) {

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

					accessibility_vars_t &vars =
					    accessibilityVars[varindexes[j]];

				    for(int k = 0 ; k < vars[nodeid].size() ; k++) {

						utility += vars[nodeid][k] * varcoeffs[j];
					}
				}
                sum += exp(mu*utility);
			}

			return log(sum);
		}
	}
}
