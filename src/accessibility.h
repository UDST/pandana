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
        vector< vector<long long> > edges,
        vector< vector<double> >  edgeweights,
        bool twoway);

    // initialize the category number with POIs at the node_id locations
    void initializeCategory(const double maxdist, const int maxitems, string category, vector<long long> node_idx);

    // find the nearest pois for all nodes in the network
    pair<vector<vector<double>>, vector<vector<int>>>
    findAllNearestPOIs(float maxradius, unsigned maxnumber,
                       string category, int graphno = 0);

    // Enhanced POI search using partial ordering optimization
    pair<vector<vector<double>>, vector<vector<int>>>
    findNearestPOIsPartial(int source_node, float maxradius, unsigned maxnumber,
                          string category, int graphno = 0);

    // Enhanced batch POI search with frontier compression concepts
    pair<vector<vector<vector<double>>>, vector<vector<vector<int>>>>
    findBatchNearestPOIs(vector<long long> source_nodes, float maxradius, unsigned maxnumber,
                        string category, int graphno = 0);

    void initializeAccVar(string category, vector<long long> node_idx,
                          vector<double> values);

    // computes the accessibility for every node in the network
    vector<double>
    getAllAggregateAccessibilityVariables(
        float radius,
        string index,
        string aggtyp,
        string decay,
        int graphno = 0);

    // Enhanced batch accessibility computation with frontier compression
    vector<vector<double>>
    getBatchAggregateAccessibilityVariables(
        vector<long long> source_nodes,
        float radius,
        string index,
        string aggtyp,
        string decay,
        int graphno = 0);

    // get nodes with a range for a specific list of source nodes
    vector<vector<pair<long long, float>>> Range(vector<long long> srcnodes, float radius, 
                                            int graphno, vector<long long> ext_ids);

    // Enhanced range query using hybrid approach with bounded relaxation concepts
    vector<vector<pair<long long, float>>> HybridRange(vector<long long> srcnodes, float radius, 
                                                  int graphno, vector<long long> ext_ids, int k_rounds = 3);

    // shortest path between two points
    vector<int> Route(int src, int tgt, int graphno = 0);

    // shortest path between list of origins and destinations
    vector<vector<int>> Routes(vector<long long> sources, vector<long long> targets,  
                               int graphno = 0);

    // shortest path distance between two points
    double Distance(int src, int tgt, int graphno = 0);
    
    // shortest path distances between list of origins and destinations
    vector<double> Distances(vector<long long> sources, vector<long long> targets,  
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

    // Helper methods for batch processing with frontier compression
    vector<vector<int>> clusterSources(const vector<long long>& sources, float cluster_radius);
    
    vector<double> processClusterWithFrontierCompression(
        const vector<int>& cluster,
        const vector<long long>& source_nodes,
        float radius,
        const string& category,
        const string& aggtyp,
        const string& decay,
        int graphno);
    
    // Helper for individual accessibility computation
    double computeIndividualAccessibility(
        long long source_node, 
        float radius,
        const string& category,
        const string& aggtyp,
        const string& decay,
        int graphno);
};
}  // namespace accessibility
}  // namespace MTC
