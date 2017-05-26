#pragma once

#include <iostream>
#include <cstdlib>
#include <vector>
#include <string>
#include "shared.h"
#include "graphalg.h"

namespace MTC {
namespace accessibility {

using std::vector;

class Accessibility {
 public:
    Accessibility(
        vector<long> nodeids, vector< vector<double> > nodexy,
        vector< vector<long> > edges, vector< vector<double> >  edgeweights,
        bool twoway);

    // set how many POI categories there will be
    void initializePOIs(
        int numcategories,
        double maxdist,
        int maxitems);

    // initialize the category number with POIs at the node_id locations
    void initializeCategory(int category, vector<long> node_ids);

    // find the nearest pois for all nodes in the network
    vector<vector<double> >
    findAllNearestPOIs(
        float maxradius,
        unsigned maxnumber,
        unsigned cat,
        int graphno = 0,
        bool return_nodeids = false);

    void initializeAccVars(int numcategories);
    void initializeAccVar(
        int index,
        vector<long> node_ids,
        vector<double> values);

    // computes the accessibility for every node in the network
    vector<double>
    getAllAggregateAccessibilityVariables(
        float radius,
        int index,
        int aggtyp,
        int decay,
        int graphno = 0);

    DistanceVec Range(int srcnode, float radius, int graphno = 0);

    vector<int> Route(int src, int tgt, int graphno = 0);
    double Distance(int src, int tgt, int graphno = 0);

    // precompute the range queries and reuse them
    void precomputeRangeQueries(float radius);

 private:
    double maxdist;
    int maxitems;

    vector<std::shared_ptr<Graphalg> > ga;

    typedef vector<vector<float> > accessibility_vars_t;
    vector<accessibility_vars_t> accessibilityVars;
    vector<accessibility_vars_t> accessibilityVarsForPOIs;

    // this stores the nodes within a certain range
    float dmsradius;
    vector<vector<DistanceVec> > dms;

    int numnodes;

    // aggregation types
    enum aggregation_types_t {
        AGG_SUM,
        AGG_AVE,
        AGG_MIN,
        AGG_25PERCENTILE,
        AGG_MEDIAN,
        AGG_75PERCENTILE,
        AGG_MAX,
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

    void addGraphalg(MTC::accessibility::Graphalg *g);

    vector<double>
    findNearestPOIs(
        int srcnode,
        float maxradius,
        unsigned maxnumber,
        unsigned cat,
        int graphno = 0,
        bool return_nodeids = false);

    // aggregate a variable within a radius
    double
    aggregateAccessibilityVariable(
        int srcnode,
        float radius,
        accessibility_vars_t &vars,
        aggregation_types_t aggtyp,
        decay_func_t gravity_func,
        int graphno = 0);

    double
    quantileAccessibilityVariable(
        DistanceVec &distances,
        accessibility_vars_t &vars,
        float quantile,
        float radius);
};
}  // namespace accessibility
}  // namespace MTC
