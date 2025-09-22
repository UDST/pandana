#pragma once

#include <vector>
#include <map>
#include <unordered_map>
#include <utility>
#include "shared.h"
#include "contraction_hierarchies/src/libch.h"

typedef unsigned int NodeID;

#define DISTANCEMULTFACT 1000.0

namespace MTC {
namespace accessibility {

using std::vector;

typedef std::map<int, float> DistanceMap;
typedef std::vector<std::pair<NodeID, float> > DistanceVec;

class Graphalg {
 public:
    Graphalg(
        int numnodes,
        vector< vector<long long> > edges, vector<double> edgeweights,
        bool twoway);

    std::vector<NodeID> Route(int src, int tgt, int threadNum = 0);

    double Distance(int src, int tgt, int threadNum = 0);

    void Range(int src, double maxdist, int threadNum,
               DistanceVec &ResultingNodes);

    // Enhanced range query using bounded relaxation + CH fallback
    void HybridRange(int src, double maxdist, int threadNum,
                     DistanceVec &ResultingNodes, int k_rounds = 3);

    DistanceMap NearestPOI(const POIKeyType &category, int src, double maxdist,
                           int number, int threadNum = 0);

    void addPOIToIndex(const POIKeyType &category, int i) {
        ch.addPOIToIndex(category, i);
    }

    void initPOIIndex(const POIKeyType &category, double maxdist, int maxitems) {
        ch.createPOIIndex(category, maxdist*DISTANCEMULTFACT, maxitems);
    }

    int numnodes;
    CH::ContractionHierarchies ch;
    
    // Store original graph for BMSSP implementation
    std::vector<std::vector<std::pair<int, double>>> adjacency_list;
    
private:
    // BMSSP algorithm implementation following Duan et al.
    struct BMSSPResult {
        double bound;
        std::vector<int> completed_nodes;
    };
    
    // Partial queue for bounded relaxation
    class PartialQueue {
    public:
        PartialQueue(double bound_b, int cap_m, int n_hint);
        void insert(int key, double val);
        void batch_prepend(const std::vector<std::pair<int, double>>& pairs);
        std::pair<std::vector<int>, double> pull();
        bool is_empty() const;
        
    private:
        std::map<double, std::vector<int>> by_val;
        std::map<int, double> cur_val;
        int cap_m;
        double bound_b;
    };
    
    BMSSPResult bmssp(int l, double bound_b, const std::vector<int>& source_set,
                      std::vector<double>& dist, std::vector<int>& pred,
                      std::vector<bool>& complete);
    
    std::pair<std::vector<int>, std::vector<int>> find_pivots(
        double bound_b, const std::vector<int>& source_set,
        std::vector<double>& dist, std::vector<int>& pred);
    
    BMSSPResult base_case(double bound_b, int source,
                          std::vector<double>& dist, std::vector<int>& pred,
                          std::vector<bool>& complete);
    
    int dfs_subtree_size(int u, const std::unordered_map<int, std::vector<int>>& children,
                         std::unordered_map<int, int>& subtree_size);
};
}  // namespace accessibility
}  // namespace MTC
