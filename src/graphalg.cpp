#include "graphalg.h"
#include <math.h>
#include <limits>
#include <algorithm>
#include <set>
#include <queue>
#include <map>
#include <unordered_set>
#include <unordered_map>
#include <cmath>
#include <functional>

namespace MTC {
namespace accessibility {
Graphalg::Graphalg(
        int numnodes, vector< vector<long long> > edges, vector<double> edgeweights,
        bool twoway) {
    this->numnodes = numnodes;
    
    // Initialize adjacency list for BMSSP implementation
    adjacency_list.resize(numnodes);
    
    // Build adjacency list from edges
    for (int i = 0; i < edges.size(); i++) {
        int u = static_cast<int>(edges[i][0]);
        int v = static_cast<int>(edges[i][1]);
        double w = edgeweights[i];
        
        adjacency_list[u].push_back(std::make_pair(v, w));
        if (twoway) {
            adjacency_list[v].push_back(std::make_pair(u, w));
        }
    }

    int num = omp_get_max_threads();
    
    FILE_LOG(logINFO) << "Generating contraction hierarchies with "
                      << num << " threads.\n";
    
    ch = CH::ContractionHierarchies(num);

    vector<CH::Node> nv;

    for (int i = 0 ; i < numnodes ; i++) {
        // CH allows you to pass in a node id, and an x and a y, and then
        // never uses it - to be clear, we don't pass it in anymore
        CH::Node n(i, 0, 0);
        nv.push_back(n);
    }

    FILE_LOG(logINFO) << "Setting CH node vector of size "
                      << nv.size() << "\n";
	
    ch.SetNodeVector(nv);

    vector<CH::Edge> ev;

    for (int i = 0 ; i < edges.size() ; i++) {
        CH::Edge e(edges[i][0], edges[i][1], i,
            edgeweights[i]*DISTANCEMULTFACT, true, twoway);
        ev.push_back(e);
    }

    FILE_LOG(logINFO) << "Setting CH edge vector of size "
                      << ev.size() << "\n";
    
    ch.SetEdgeVector(ev);
    ch.RunPreprocessing();
}

// PartialQueue implementation following Rust reference
Graphalg::PartialQueue::PartialQueue(double bound_b, int cap_m, int n_hint) 
    : cap_m(std::max(cap_m, 1)), bound_b(bound_b) {
}

void Graphalg::PartialQueue::insert(int key, double val) {
    const double EPS = 1e-12;
    if (!(val < bound_b - EPS)) return;
    
    auto it = cur_val.find(key);
    if (it != cur_val.end()) {
        double old_val = it->second;
        if (val + EPS >= old_val) return; // no improvement
        
        // Remove old entry
        auto val_it = by_val.find(old_val);
        if (val_it != by_val.end()) {
            auto& vec = val_it->second;
            auto pos = std::find(vec.begin(), vec.end(), key);
            if (pos != vec.end()) {
                vec.erase(pos);
            }
            if (vec.empty()) {
                by_val.erase(val_it);
            }
        }
    }
    
    by_val[val].push_back(key);
    cur_val[key] = val;
}

void Graphalg::PartialQueue::batch_prepend(const std::vector<std::pair<int, double>>& pairs) {
    for (const auto& p : pairs) {
        insert(p.first, p.second);
    }
}

std::pair<std::vector<int>, double> Graphalg::PartialQueue::pull() {
    std::vector<int> picked;
    std::vector<double> to_remove;
    
    for (auto it = by_val.begin(); it != by_val.end(); ++it) {
        double val = it->first;
        std::vector<int>& keys = it->second;
        if (picked.size() >= cap_m) break;
        
        int take = std::min(cap_m - static_cast<int>(picked.size()), static_cast<int>(keys.size()));
        for (int i = 0; i < take; i++) {
            picked.push_back(keys[i]);
        }
        
        if (take == keys.size()) {
            to_remove.push_back(val);
        } else {
            // Remove taken keys
            keys.erase(keys.begin(), keys.begin() + take);
        }
    }
    
    // Clean up empty entries
    for (double val : to_remove) {
        by_val.erase(val);
    }
    
    // Remove picked keys from cur_val
    for (int key : picked) {
        cur_val.erase(key);
    }
    
    double x = bound_b;
    if (!by_val.empty()) {
        x = by_val.begin()->first;
    }
    
    return std::make_pair(picked, x);
}

bool Graphalg::PartialQueue::is_empty() const {
    return cur_val.empty();
}

// Base case implementation following Rust reference
Graphalg::BMSSPResult Graphalg::base_case(double bound_b, int source,
                                          std::vector<double>& dist, std::vector<int>& pred,
                                          std::vector<bool>& complete) {
    const double EPS = 1e-12;
    
    // Calculate k parameter (similar to Rust implementation)
    int n = numnodes;
    double ln = std::log(std::max(n, 2));
    int k = std::max(1, static_cast<int>(std::pow(ln, 1.0/3.0)));
    
    std::vector<int> u0;
    std::priority_queue<std::pair<double, int>, std::vector<std::pair<double, int>>, std::greater<std::pair<double, int>>> heap;
    std::unordered_set<int> in_heap;
    
    heap.push(std::make_pair(dist[source], source));
    in_heap.insert(source);
    
    while (!heap.empty()) {
        std::pair<double, int> top = heap.top();
        double d = top.first;
        int u = top.second;
        heap.pop();
        in_heap.erase(u);
        
        if (d >= bound_b - EPS) break;
        
        if (std::find(u0.begin(), u0.end(), u) == u0.end()) {
            u0.push_back(u);
            complete[u] = true;
        }
        
        if (u0.size() >= k + 1) break;
        
        // Relax neighbors
        for (size_t idx = 0; idx < adjacency_list[u].size(); ++idx) {
            int v = adjacency_list[u][idx].first;
            double w = adjacency_list[u][idx].second;
            double cand = d + w;
            if (cand < bound_b - EPS) {
                bool improve = cand + EPS < dist[v];
                bool tie = std::abs(cand - dist[v]) <= EPS;
                
                if (improve || (tie && (pred[v] == -1 || u < pred[v]))) {
                    dist[v] = cand;
                    pred[v] = u;
                }
                
                if (in_heap.find(v) == in_heap.end()) {
                    heap.push(std::make_pair(dist[v], v));
                    in_heap.insert(v);
                }
            }
        }
    }
    
    if (u0.size() <= k) {
        BMSSPResult result;
        result.bound = bound_b;
        result.completed_nodes = u0;
        return result;
    } else {
        // Find max distance and return nodes strictly smaller
        double max_dist = 0.0;
        for (int v : u0) {
            if (std::isfinite(dist[v])) {
                max_dist = std::max(max_dist, dist[v]);
            }
        }
        
        std::vector<int> u_final;
        for (int v : u0) {
            if (dist[v] < max_dist - EPS) {
                u_final.push_back(v);
            }
        }
        
        BMSSPResult result;
        result.bound = max_dist;
        result.completed_nodes = u_final;
        return result;
    }
}

// Helper function for DFS subtree size calculation
int Graphalg::dfs_subtree_size(int u, const std::unordered_map<int, std::vector<int>>& children,
                               std::unordered_map<int, int>& subtree_size) {
    auto it = subtree_size.find(u);
    if (it != subtree_size.end()) return it->second;
    
    int total = 1;
    auto children_it = children.find(u);
    if (children_it != children.end()) {
        for (int v : children_it->second) {
            total += dfs_subtree_size(v, children, subtree_size);
        }
    }
    subtree_size[u] = total;
    return total;
}

// FindPivots implementation following Rust reference
std::pair<std::vector<int>, std::vector<int>> Graphalg::find_pivots(
    double bound_b, const std::vector<int>& source_set,
    std::vector<double>& dist, std::vector<int>& pred) {
    
    const double EPS = 1e-12;
    
    // Calculate k parameter
    int n = numnodes;
    double ln = std::log(std::max(n, 2));
    int k = std::max(1, static_cast<int>(std::pow(ln, 1.0/3.0)));
    
    std::set<int> w_set;
    std::vector<int> current = source_set;
    
    // Add source set to W
    for (int x : current) {
        w_set.insert(x);
    }
    
    std::vector<std::vector<int>> layers;
    layers.push_back(current);
    
    // k rounds of relaxation
    for (int round = 0; round < k; ++round) {
        std::vector<int> next_layer;
        
        for (int u : layers.back()) {
            double du = dist[u];
            
            for (size_t idx = 0; idx < adjacency_list[u].size(); ++idx) {
                int v = adjacency_list[u][idx].first;
                double weight = adjacency_list[u][idx].second;
                double cand = du + weight;
                
                if (cand < bound_b - EPS) {
                    bool improve = cand + EPS < dist[v];
                    bool tie = std::abs(cand - dist[v]) <= EPS;
                    
                    if (improve || (tie && (pred[v] == -1 || u < pred[v]))) {
                        dist[v] = cand;
                        pred[v] = u;
                    }
                    
                    if (w_set.find(v) == w_set.end()) {
                        next_layer.push_back(v);
                        w_set.insert(v);
                    }
                }
            }
        }
        
        // Check for excessive growth
        if (w_set.size() > k * source_set.size()) {
            std::vector<int> w_vec(w_set.begin(), w_set.end());
            return std::make_pair(source_set, w_vec);
        }
        
        layers.push_back(next_layer);
        if (next_layer.empty()) break;
    }
    
    // Build forest and find pivots
    std::vector<int> w_vec(w_set.begin(), w_set.end());
    std::unordered_set<int> w_hash(w_vec.begin(), w_vec.end());
    
    // Build parent relationships
    std::unordered_map<int, int> parent;
    std::unordered_map<int, std::vector<int>> children;
    std::unordered_map<int, int> indegree;
    
    for (int u : w_vec) {
        indegree[u] = 0;
        children[u] = std::vector<int>();
    }
    
    for (int u : w_vec) {
        double du = dist[u];
        
        for (size_t idx = 0; idx < adjacency_list[u].size(); ++idx) {
            int v = adjacency_list[u][idx].first;
            double weight = adjacency_list[u][idx].second;
            if (w_hash.find(v) == w_hash.end()) continue;
            
            double cand = du + weight;
            if (std::abs(cand - dist[v]) <= EPS) {
                // Edge belongs to forest
                auto it = parent.find(v);
                if (it == parent.end() || u < it->second) {
                    if (it != parent.end()) {
                        // Remove old parent relationship
                        int old_parent = it->second;
                        auto& old_children = children[old_parent];
                        old_children.erase(std::find(old_children.begin(), old_children.end(), v));
                        indegree[v]--;
                    }
                    parent[v] = u;
                    children[u].push_back(v);
                    indegree[v]++;
                }
            }
        }
    }
    
    // Calculate subtree sizes using DFS
    std::unordered_map<int, int> subtree_size;
    
    // Find pivots: roots in S∩W with subtree size >= k
    std::vector<int> pivots;
    std::unordered_set<int> source_hash(source_set.begin(), source_set.end());
    
    for (int u : source_set) {
        if (w_hash.find(u) == w_hash.end()) continue;
        
        bool is_root = (indegree[u] == 0);
        if (is_root) {
            int size = dfs_subtree_size(u, children, subtree_size);
            if (size >= k) {
                pivots.push_back(u);
            }
        }
    }
    
    return std::make_pair(pivots, w_vec);
}

// Main BMSSP recursive function following Rust reference
Graphalg::BMSSPResult Graphalg::bmssp(int l, double bound_b, const std::vector<int>& source_set,
                                      std::vector<double>& dist, std::vector<int>& pred,
                                      std::vector<bool>& complete) {
    const double EPS = 1e-12;
    
    if (source_set.empty()) {
        BMSSPResult result;
        result.bound = bound_b;
        result.completed_nodes = std::vector<int>();
        return result;
    }
    
    if (l == 0) {
        return base_case(bound_b, source_set[0], dist, pred, complete);
    }
    
    std::pair<std::vector<int>, std::vector<int>> pivots_result = find_pivots(bound_b, source_set, dist, pred);
    std::vector<int> pivots = pivots_result.first;
    std::vector<int> w_set = pivots_result.second;
    
    // Initialize partial queue
    int m = std::max(static_cast<int>(source_set.size()), 1);
    PartialQueue pq(bound_b, m, numnodes);
    
    for (int x : pivots) {
        pq.insert(x, dist[x]);
    }
    
    std::vector<int> u_total;
    double last_bi_prime = bound_b;
    
    while (!pq.is_empty()) {
        std::pair<std::vector<int>, double> pull_result = pq.pull();
        std::vector<int> si = pull_result.first;
        double bi = pull_result.second;
        
        if (si.empty()) continue;
        
        // Recursive call
        BMSSPResult bmssp_result = bmssp(l - 1, bi, si, dist, pred, complete);
        double bi_prime = bmssp_result.bound;
        std::vector<int> ui = bmssp_result.completed_nodes;
        
        // Mark Ui as complete
        for (int u : ui) {
            complete[u] = true;
        }
        u_total.insert(u_total.end(), ui.begin(), ui.end());
        last_bi_prime = bi_prime;
        
        // Relax from Ui and reseed queue
        std::vector<std::pair<int, double>> to_batch;
        
        for (int u : ui) {
            double du = dist[u];
            
            for (size_t idx = 0; idx < adjacency_list[u].size(); ++idx) {
                int v = adjacency_list[u][idx].first;
                double weight = adjacency_list[u][idx].second;
                double cand = du + weight;
                
                // Relax if better or tie with smaller parent
                bool improve = cand + EPS < dist[v];
                bool tie = std::abs(cand - dist[v]) <= EPS;
                
                if (improve || (tie && (pred[v] == -1 || u < pred[v]))) {
                    dist[v] = cand;
                    pred[v] = u;
                }
                
                if (cand < bound_b - EPS) {
                    if (cand >= bi - EPS) {
                        pq.insert(v, cand);
                    } else if (cand >= bi_prime - EPS) {
                        to_batch.push_back(std::make_pair(v, cand));
                    }
                }
            }
        }
        
        if (!to_batch.empty()) {
            pq.batch_prepend(to_batch);
        }
    }
    
    // Include reachable W vertices
    std::unordered_set<int> u_total_set(u_total.begin(), u_total.end());
    for (int x : w_set) {
        if (dist[x] < bound_b - EPS && u_total_set.find(x) == u_total_set.end()) {
            u_total.push_back(x);
            complete[x] = true;
        }
    }
    
    BMSSPResult result;
    result.bound = bound_b;
    result.completed_nodes = u_total;
    return result;
}

std::vector<NodeID> Graphalg::Route(int src, int tgt, int threadNum) {
    std::vector<NodeID> ResultingPath;

    CH::Node src_node(src, 0, 0);
    CH::Node tgt_node(tgt, 0, 0);

    ch.computeShortestPath(
        src_node,
        tgt_node,
        ResultingPath,
        threadNum);

    // TODO: return the mileage as well as the route
    return ResultingPath;
}

double Graphalg::Distance(int src, int tgt, int threadNum) {
    // TODO: we should be able to do this without computing 
    // the route which is wasteful
    CH::Node src_node(src, 0, 0);
    CH::Node tgt_node(tgt, 0, 0);

    unsigned int length = ch.computeLengthofShortestPath(
        src_node,
        tgt_node,
        threadNum);

    return static_cast<double>(length) /
        static_cast<double>(DISTANCEMULTFACT);
}

void Graphalg::Range(int src, double maxdist, int threadNum,
                     DistanceVec &ResultingNodes) {
    
    const unsigned int maxdist_scaled = 
        static_cast<unsigned int>(maxdist * DISTANCEMULTFACT);

    CH::Node src_node(src, 0, 0);
    std::vector<std::pair<NodeID, unsigned> > tmp;
    ch.computeReachableNodesWithin(
        src_node, maxdist_scaled, tmp, threadNum);

    ResultingNodes.clear();
    for (int i = 0 ; i < tmp.size() ; i++) {
        std::pair<NodeID, float> node(
            tmp[i].first, 
            static_cast<float>(tmp[i].second) / 
            static_cast<float>(DISTANCEMULTFACT));

        ResultingNodes.push_back(node);
    }
}

void Graphalg::HybridRange(int src, double maxdist, int threadNum,
                          DistanceVec &ResultingNodes, int k_rounds) {
    // BMSSP implementation following Duan et al. algorithm
    ResultingNodes.clear();
    
    const double INF = std::numeric_limits<double>::infinity();
    const double EPS = 1e-12;
    
    // Initialize distance and predecessor arrays
    std::vector<double> dist(numnodes, INF);
    std::vector<int> pred(numnodes, -1);
    std::vector<bool> complete(numnodes, false);
    
    // Initialize source
    dist[src] = 0.0;
    complete[src] = true;
    
    // Calculate algorithm parameters
    int n = numnodes;
    double ln = std::log(std::max(n, 2));
    int t = std::max(1, static_cast<int>(std::pow(ln, 2.0/3.0)));
    int lmax = std::max(1, static_cast<int>(std::ceil(ln / t)));
    
    // Decide whether to use BMSSP or fall back to CH
    bool use_bmssp = (k_rounds > 0 && maxdist < 20.0 && numnodes > 100);
    
    if (use_bmssp) {
        // Run BMSSP algorithm
        std::vector<int> source_set;
        source_set.push_back(src);
        BMSSPResult final_result = bmssp(lmax, maxdist, source_set, dist, pred, complete);
        double final_bound = final_result.bound;
        std::vector<int> completed_nodes = final_result.completed_nodes;
        
        // Collect results within distance bound
        for (int i = 0; i < numnodes; ++i) {
            if (std::isfinite(dist[i]) && dist[i] <= maxdist) {
                ResultingNodes.push_back(std::make_pair(static_cast<NodeID>(i), static_cast<float>(dist[i])));
            }
        }
        
        // If BMSSP found very few results, fall back to CH
        if (ResultingNodes.size() < 3) {
            ResultingNodes.clear();
            use_bmssp = false;
        }
    }
    
    if (!use_bmssp) {
        // Fall back to standard CH range query
        const unsigned int maxdist_scaled = static_cast<unsigned int>(maxdist * DISTANCEMULTFACT);
        CH::Node src_node(src, 0, 0);
        std::vector<std::pair<NodeID, unsigned>> ch_results;
        ch.computeReachableNodesWithin(src_node, maxdist_scaled, ch_results, threadNum);
        
        for (const auto& ch_result : ch_results) {
            ResultingNodes.push_back(std::make_pair(ch_result.first, 
                static_cast<float>(ch_result.second) / DISTANCEMULTFACT));
        }
    }
}

DistanceMap
Graphalg::NearestPOI(const POIKeyType &category, int src, double maxdist, int number,
                     int threadNum) {
    DistanceMap dm;

    std::vector<CH::BucketEntry> ResultingNodes;
    ch.getNearestWithUpperBoundOnDistanceAndLocations(
        category,
        src,
        maxdist*DISTANCEMULTFACT,
        number,
        ResultingNodes,
        threadNum);

    for (int i = 0 ; i < ResultingNodes.size() ; i++) {
        dm[ResultingNodes[i].node] =
            static_cast<float>(ResultingNodes[i].distance) /
            static_cast<float>(DISTANCEMULTFACT);
    }

    return dm;
}
}  // namespace accessibility
}  // namespace MTC