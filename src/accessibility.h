#pragma once

#include <iostream>
#include <cstdlib>
#include <vector>
#include <string>
#include <utility>
#include <map>
#include "shared.h"
#include "graphalg.h"

namespace MTC {
namespace accessibility {

using std::vector;
using std::string;
using std::set;
using std::map;

class Accessibility {
 public:
    Accessibility(
        int numnodes,
        vector< vector<long> > edges,
        vector< vector<double> >  edgeweights,
        bool twoway);

    // initialize the category number with POIs at the node_id locations
    void initializeCategory(const double maxdist, const int maxitems, string category, vector<long> node_idx);

    // find the nearest pois for all nodes in the network
    pair<vector<vector<double>>, vector<vector<int>>>
    findAllNearestPOIs(float maxradius, unsigned maxnumber,
                       string category, int graphno = 0);

    void initializeAccVar(string category, vector<long> node_idx,
                          vector<double> values);

    // computes the accessibility for every node in the network
    vector<double>
    getAllAggregateAccessibilityVariables(
        float radius,
        string index,
        string aggtyp,
        string decay,
        int graphno = 0);

    // get nodes with the range
    DistanceVec Range(int srcnode, float radius, int graphno = 0);

    // shortest path between two points
    vector<int> Route(int src, int tgt, int graphno = 0);

    // shortest path between list of origins and destinations
    vector<vector<int>> Routes(vector<long> sources, vector<long> targets,  
                             int graphno = 0);

    // shortest path distance between two points
    double Distance(int src, int tgt, int graphno = 0);
    
    // shortest path distances between list of origins and destinations
    vector<double> Distances(vector<long> sources, vector<long> targets,  
                             int graphno = 0);

    // precompute the range queries and reuse them
    void precomputeRangeQueries(float radius);

    // aggregation types
    vector<string> aggregations;

    // decay types
    vector<string> decays;

 private:
    double maxdist;
    int maxitems;

    // a vector of graphs - all these graphs share the same nodes, and
    // thus it shares the same accessibility_vars_t as well -
    // this is used e.g. for road networks where we have congestion
    // by time of day
    vector<std::shared_ptr<Graphalg> > ga;

    // accessibility_vars_t is a vector of floating point values
    // assigned to each node - the first level of the data structure
    // is dereferenced by node index
    typedef vector<vector<float> > accessibility_vars_t;
    map<string, accessibility_vars_t> accessibilityVars;
    // this is a map for pois so we can keep track of how many
    // pois there are at each node - for now all the values are
    // set to one, but I can imagine using floating point values
    // here eventually - e.g. find the 3 nearest values similar to
    // a knn tree in 2D space
    std::map<POIKeyType, accessibility_vars_t> accessibilityVarsForPOIs;

    // this stores the nodes within a certain range - we have the option
    // of precomputing all the nodes in a radius if we're going to make
    // lots of aggregation queries on the same network
    float dmsradius;
    vector<vector<DistanceVec> > dms;

    int numnodes;

    void addGraphalg(MTC::accessibility::Graphalg *g);

    vector<pair<double, int>>
    findNearestPOIs(int srcnode, float maxradius, unsigned maxnumber,
                    string cat, int graphno = 0);

    // aggregate a variable within a radius
    double
    aggregateAccessibilityVariable(
        int srcnode,
        float radius,
        accessibility_vars_t &vars,
        string aggtyp,
        string gravity_func,
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
