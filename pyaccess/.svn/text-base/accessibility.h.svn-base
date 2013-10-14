#pragma once

#include <iostream>
#include <cstdlib>
#include <vector>
#include "shared.h"
#include "nearestneighbor.h"
#include "graphalg.h"
#include "omp.h"

using namespace std;

namespace MTC {
	namespace accessibility {

		// XXX some of these agg types aren't implemented
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
		
		// points of interest categories
		enum POI_category_t {
			POI_COFFEESHOPS,
			POI_RESTAURANTS,
			POI_SHOPPING,
			POI_GROCERY,
			POI_BANKS,
			POI_PARKS,
			POI_SCHOOLS,
			POI_BOOKSTORES,
			POI_ENTERTAINMENT,
			POI_MAXVAL
		};

		// entropy categories
		enum ENTROPY_category_t {
			ENTROPY_JOBSHOUSING,
			ENTROPY_RESNONRES,
			ENTROPY_BUILDINGTYP,
			ENTROPY_JOBSECTOR,
			ENTROPY_HOUSINiGTYPES,
			ENTROPY_MAXVAL
		};

		typedef std::vector<std::vector<float> > accessibility_vars_t;
		
		typedef struct AccVarDef {
			std::string tblname;
			std::string varname;
			inline bool operator==(const AccVarDef &ref)
			{
				if(tblname != ref.tblname) return false;
				if(varname != ref.varname) return false;
				return true;
			}
		} acc_var_def_t;

		class DLLExport Accessibility
		{
		public:
			Accessibility(int numnodes=0);

			// aggregate a variable within a radius
			double aggregateAccessibilityVariable(int srcnode, float radius, 
										accessibility_vars_t &vars,
										aggregation_types_t aggtyp, 
										decay_func_t gravity_func,
										int graphno=0);
			
			// computes the accessibility for every node in the network
			std::vector<double>
			getAllAggregateAccessibilityVariables(float radius, int index,
								aggregation_types_t aggtyp, decay_func_t decay,
								int graphno=0);

            // this simulates a nested choice model as it moves through the graph
            // varindexes and varcoefficients give the variables that are added to the utility
            // distcoeff is multiplied by the distance and added to utility, asc is just added
            // denom and nestdenom are used to compute probabilities rather than just logsums
            // mu is the nesting coefficient that the utility gets multiplied by
			std::vector<double>
			getAllModelResults(float radius, int numvars, int *varindexes, float *varcoeffs,
                                float distcoeff, float asc, float denom, float nestdenom, float mu, int graphno);

		    double
		    modelResult(int srcnode, float radius, int numvars, int *varindexes, float *varcoeffs,
                        float distcoeff, float asc, float denom, float nestdenom, float mu, int gno);

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
											float maxradius, int maxnumber, 
											POI_category_t cat,
											int graphno=0);
			std::vector<double> findAllNearestPOIs(float maxradius,
											POI_category_t cat);

            DistanceVec Range(int srcnode, float radius, int graphno=0);

			// leverage the POI queries to create an openwalkscore
			double getOpenWalkscore(int srcnode);
			std::vector<double> getAllOpenWalkscores();

			vector<accessibility_vars_t>	accessibilityVars;
			vector<accessibility_vars_t>	accessibilityVarsForPOIs;

			std::vector<std::shared_ptr<Graphalg> > ga;

			// a little hackish but you can precompute 
			// the range queries and reuse them
			void precomputeRangeQueries(float radius);
			float dmsradius;
			std::vector<std::vector<DistanceVec> > dms;

			int numnodes;

			// this is where we set the nodes - this is only useful for serialization
			std::vector<float> xVec;
			std::vector<float> yVec;
			std::vector<int> ids;

			template<class Archive>
			void serialize(Archive & ar, const unsigned int /* file_version */){
					ar & dmsradius & dms & numnodes & xVec & yVec & ids;
			}		
			bool saveCSV(std::string filename);
			bool saveFile(std::string filename);
			bool loadFile(std::string filename);

		private:

			int compute_num_blocks(DistanceVec &distances);
			double compute_centrality(int srcnode, DistanceVec &distances,
											 int graphno=0);
			double compute_street_design_var(DistanceVec &distances, 
											 std::string type, float radius,
											 int graphno=0);			
		};
	}
}

