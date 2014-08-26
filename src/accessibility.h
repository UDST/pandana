#pragma once

#include <iostream>
#include <cstdlib>
#include <vector>
#include "shared.h"
#include "nearestneighbor.h"
#include "graphalg.h"

using namespace std;

namespace MTC {
	namespace accessibility {

		// TODO some of these agg types aren't implemented
		// aggregation types
		enum aggregation_types_t {
			AGG_SUM,
			AGG_AVE,
			AGG_MIN,
			AGG_MAX,
			AGG_MEDIAN,
			AGG_STDDEV,
			AGG_COUNT,
			AGG_MAXVAL
		};

		// decay functins for aggregation
		enum decay_func_t {
			DECAY_EXP,
			DECAY_LINEAR,
			DECAY_FLAT,
			DECAY_MAXVAL
		};

		typedef std::vector<std::vector<float> > accessibility_vars_t;

		#ifdef _WIN32
			class DLLExport Accessibility
		#else
			class Accessibility
		#endif
		{
		public:
			Accessibility(int numnodes=0);

			// aggregate a variable within a radius
			double aggregateAccessibilityVariable(int srcnode, float radius,
		        accessibility_vars_t &vars, aggregation_types_t aggtyp,
		        decay_func_t gravity_func, int graphno=0);

			// computes the accessibility for every node in the network
			std::vector<double>
			getAllAggregateAccessibilityVariables(float radius, int index,
			    aggregation_types_t aggtyp, decay_func_t decay, int graphno=0);

            // this simulates a nested choice model as it moves through the
            // graph varindexes and varcoefficients give the variables that
            // are added to the utility distcoeff is multiplied by the
            // distance and added to utility, asc is just added denom and
            // nestdenom are used to compute probabilities rather than just
            // logsums mu is the nesting coefficient that the utility gets
            // multiplied by
			std::vector<double>
			getAllModelResults(float radius, int numvars, int *varindexes,
			    float *varcoeffs, float distcoeff, float asc, float denom,
			    float nestdenom, float mu, int graphno);

		    double
		    modelResult(int srcnode, float radius, int numvars, int *varindexes,
		        float *varcoeffs, float distcoeff, float asc, float denom,
		        float nestdenom, float mu, int gno);

			// compute a variable having to do with the street network
			double computeDesignVariable(int srcnode, float radius,
										 std::string type,
										 int graphno=0);

			void initializeAccVars(int numcategories);
            void initializeAccVar(int index, accessibility_vars_t &vars);

			// look for the closest points of interest
			void initializePOIs(int numcategories, double maxdist,
			    int maxitems);
			void initializeCategory(int category, accessibility_vars_t &vars);

			std::vector<float> findNearestPOIs(int srcnode,
			    float maxradius, unsigned maxnumber, unsigned cat,
			    int graphno=0);
			std::vector<std::vector<float> >
			    findAllNearestPOIs(float maxradius, unsigned maxnumber,
			            unsigned cat, int graphno=0);

            DistanceVec Range(int srcnode, float radius, int graphno=0);

			vector<accessibility_vars_t>	accessibilityVars;
			vector<accessibility_vars_t>	accessibilityVarsForPOIs;

			std::vector<std::shared_ptr<Graphalg> > ga;

			// precompute the range queries and reuse them
			void precomputeRangeQueries(float radius);
			float dmsradius;
			std::vector<std::vector<DistanceVec> > dms;

			int numnodes;

		private:
			double compute_centrality(int srcnode, DistanceVec &distances,
											 int graphno=0);
			double compute_street_design_var(DistanceVec &distances,
											 std::string type, float radius,
											 int graphno=0);
		};
	}
}

