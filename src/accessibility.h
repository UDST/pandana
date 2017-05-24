#pragma once

#include <iostream>
#include <cstdlib>
#include <vector>
#include <string>
#include "./shared.h"
#include "./graphalg.h"

namespace MTC {
namespace accessibility {

typedef std::vector<std::vector<float> > accessibility_vars_t;

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

class Accessibility {
 public:
    explicit Accessibility(int numnodes = 0);

    void addGraphalg(MTC::accessibility::Graphalg *g);

    // set how many POI categories there will be
    void initializePOIs(
        int numcategories,
        double maxdist,
        int maxitems);

    // initialize the category number with POIs at the node_id locations
    void initializeCategory(int category, std::vector<int> node_ids);

    // find the nearest pois for all nodes in the network
    std::vector<std::vector<float> >
    findAllNearestPOIs(
        float maxradius,
        unsigned maxnumber,
        unsigned cat,
        int graphno = 0,
        bool return_nodeids = false);

    void initializeAccVars(int numcategories);
    void initializeAccVar(int index, accessibility_vars_t &vars);

    // computes the accessibility for every node in the network
    std::vector<double>
    getAllAggregateAccessibilityVariables(
        float radius,
        int index,
        aggregation_types_t aggtyp,
        decay_func_t decay,
        int graphno = 0);

    DistanceVec Range(int srcnode, float radius, int graphno = 0);

    // precompute the range queries and reuse them
    void precomputeRangeQueries(float radius);

 private:
    std::vector<std::shared_ptr<Graphalg> > ga;

    vector<accessibility_vars_t>    accessibilityVars;
    vector<accessibility_vars_t>    accessibilityVarsForPOIs;

    // this stores the nodes within a certain range
    float dmsradius;
    std::vector<std::vector<DistanceVec> > dms;

    int numnodes;

    std::vector<float>
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
