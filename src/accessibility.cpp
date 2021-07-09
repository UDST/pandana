#include "accessibility.h"
#include <algorithm>
#include <cmath>
#include <functional>
#include <unordered_map>
#include <utility>
#include "graphalg.h"

namespace MTC {
namespace accessibility {

using std::string;
using std::vector;
using std::pair;
using std::make_pair;

typedef std::pair<double, int> distance_node_pair;
bool distance_node_pair_comparator(const distance_node_pair& l,
                                   const distance_node_pair& r)
    { return l.first < r.first; }


Accessibility::Accessibility(
        int numnodes,
        vector< vector<long>> edges,
        vector< vector<double>>  edgeweights,
        bool twoway) {

    this->aggregations.reserve(9);
    this->aggregations.push_back("sum");
    this->aggregations.push_back("mean");
    this->aggregations.push_back("min");
    this->aggregations.push_back("25pct");
    this->aggregations.push_back("median");
    this->aggregations.push_back("75pct");
    this->aggregations.push_back("max");
    this->aggregations.push_back("std");
    this->aggregations.push_back("count");

    this->decays.reserve(3);
    this->decays.push_back("exp");
    this->decays.push_back("linear");
    this->decays.push_back("flat");

    for (int i = 0 ; i < edgeweights.size() ; i++) {
        this->addGraphalg(new Graphalg(numnodes, edges, edgeweights[i],
                          twoway));
    }

    this->numnodes = numnodes;
    this->dmsradius = -1;
}


void Accessibility::addGraphalg(MTC::accessibility::Graphalg *g) {
    std::shared_ptr<MTC::accessibility::Graphalg>ptr(g);
    this->ga.push_back(ptr);
}


void
Accessibility::precomputeRangeQueries(float radius) {
    dms.resize(ga.size());
    for (int i = 0 ; i < ga.size() ; i++) {
        dms[i].resize(numnodes);
    }

    #pragma omp parallel
    {
    #pragma omp for schedule(guided)
    for (int i = 0 ; i < numnodes ; i++) {
        for (int j = 0 ; j < ga.size() ; j++) {
            ga[j]->Range(
                i,
                radius,
                omp_get_thread_num(),
                dms[j][i]);
        }
    }
    }
    dmsradius = radius;
}


vector<vector<pair<long, float>>>
Accessibility::Range(vector<long> srcnodes, float radius, int graphno, 
                     vector<long> ext_ids) {

    // Set up a mapping between the external node ids and internal ones
    std::unordered_map<long, int> int_ids(ext_ids.size());
    for (int i = 0; i < ext_ids.size(); i++) {
        int_ids.insert(pair<long, int>(ext_ids[i], i));
    }
    
    // use cached results if available
    vector<DistanceVec> dists(srcnodes.size());
    if (dmsradius > 0 && radius <= dmsradius) {
        for (int i = 0; i < srcnodes.size(); i++) {
            dists[i] = dms[graphno][int_ids[srcnodes[i]]];
        }
    }
    else {
        #pragma omp parallel
        #pragma omp for schedule(guided)
        for (int i = 0; i < srcnodes.size(); i++) {
            ga[graphno]->Range(int_ids[srcnodes[i]], radius,
                omp_get_thread_num(), dists[i]);
        }
    }
    
    // todo: check that results are returned from cache correctly
    // todo: check that performing an aggregation creates cache

    // Convert back to external node ids
    vector<vector<pair<long, float>>> output(dists.size());
    for (int i = 0; i < dists.size(); i++) {
        output[i].resize(dists[i].size());
        for (int j = 0; j < dists[i].size(); j++) {
            output[i][j] = std::make_pair(ext_ids[dists[i][j].first], 
                                          dists[i][j].second);
        }
    }
    return output;
}


vector<int>
Accessibility::Route(int src, int tgt, int graphno) {
    vector<NodeID> ret = this->ga[graphno]->Route(src, tgt);
    return vector<int> (ret.begin(), ret.end());
}


vector<vector<int>>
Accessibility::Routes(vector<long> sources, vector<long> targets, int graphno) {

    int n = std::min(sources.size(), targets.size()); // in case lists don't match
    vector<vector<int>> routes(n);

    #pragma omp parallel
    #pragma omp for schedule(guided)
    for (int i = 0 ; i < n ; i++) {
        vector<NodeID> ret = this->ga[graphno]->Route(sources[i], targets[i], 
            omp_get_thread_num());
        routes[i] = vector<int> (ret.begin(), ret.end());
    }
    return routes;
}


double
Accessibility::Distance(int src, int tgt, int graphno) {
    return this->ga[graphno]->Distance(src, tgt);
}


vector<double>
Accessibility::Distances(vector<long> sources, vector<long> targets, int graphno) {                       
    
    int n = std::min(sources.size(), targets.size()); // in case lists don't match
    vector<double> distances(n);
    
    #pragma omp parallel
    #pragma omp for schedule(guided)
    for (int i = 0 ; i < n ; i++) {
        distances[i] = this->ga[graphno]->Distance(
            sources[i], 
            targets[i], 
            omp_get_thread_num());
    }
    return distances;
}


/*
#######################
POI QUERIES
#######################
*/


void Accessibility::initializeCategory(const double maxdist, const int maxitems,
                                       string category, vector<long> node_idx)
{
    accessibility_vars_t av;
    av.resize(this->numnodes);

    this->maxdist = maxdist;
    this->maxitems = maxitems;

    // initialize for all subgraphs
    for (int i = 0 ; i < ga.size() ; i++) {
        ga[i]->initPOIIndex(category, this->maxdist, this->maxitems);
        // initialize for each node
        for (int j = 0 ; j < node_idx.size() ; j++) {
            int node_id = node_idx[j];

            ga[i]->addPOIToIndex(category, node_id);
            assert(node_id << av.size());
            av[node_id].push_back(j);
        }
    }
    accessibilityVarsForPOIs[category] = av;
}


/* the return_nodeidx parameter determines whether to
   return the nodeidx where the poi was found rather than
   the distances - you can call this twice - once for the
   distances and then again for the node idx */
vector<pair<double, int>>
Accessibility::findNearestPOIs(int srcnode, float maxradius, unsigned number,
                               string cat, int gno)
{
    DistanceMap distancesmap = ga[gno]->NearestPOI(cat, srcnode,
        maxradius, number, omp_get_thread_num());

    vector<distance_node_pair> distance_node_pairs;
    std::map<POIKeyType, accessibility_vars_t>::iterator cat_for_pois = 
        accessibilityVarsForPOIs.find(cat);
    if(cat_for_pois == accessibilityVarsForPOIs.end())
        return distance_node_pairs;
    
    accessibility_vars_t &vars = cat_for_pois->second;

    /* need to account for the possibility of having
     multiple locations at single node */
    for (DistanceMap::const_iterator itDist = distancesmap.begin();
       itDist != distancesmap.end();
       ++itDist) {
      int nodeid = itDist->first;
      double distance = itDist->second;

      for (int i = 0 ; i < vars[nodeid].size() ; i++) {
          distance_node_pairs.push_back(
             make_pair(distance, vars[nodeid][i]));
      }
    }

    std::sort(distance_node_pairs.begin(), distance_node_pairs.end(),
            distance_node_pair_comparator);

    return distance_node_pairs;
}


/* the return_nodeds param is described above */
pair<vector<vector<double>>, vector<vector<int>>>
Accessibility::findAllNearestPOIs(float maxradius, unsigned num_of_pois,
                                  string category,int gno)
{
    vector<vector<double>>
        dists(numnodes, vector<double> (num_of_pois));

    vector<vector<int>>
        poi_ids(numnodes, vector<int> (num_of_pois));

    #pragma omp parallel for
    for (int i = 0 ; i < numnodes ; i++) {
        vector<pair<double, int>> d = findNearestPOIs(
            i,
            maxradius,
            num_of_pois,
            category,
            gno);
        for (int j = 0 ; j < num_of_pois ; j++) {
            if (j < d.size()) {
                dists[i][j] = d[j].first;
                poi_ids[i][j] = d[j].second;
            } else {
                dists[i][j] = -1;
                poi_ids[i][j] = -1;
            }
        }
    }
    return make_pair(dists, poi_ids);
}


/*
#######################
AGGREGATION/ACCESSIBILITY QUERIES
#######################
*/


void Accessibility::initializeAccVar(
    string category,
    vector<long> node_idx,
    vector<double> values) {
    accessibility_vars_t av;
    av.resize(this->numnodes);
    for (int i = 0 ; i < node_idx.size() ; i++) {
        int node_id = node_idx[i];
        double val = values[i];

        assert(node_id << av.size());
        av[node_id].push_back(val);
    }
    accessibilityVars[category] = av;
}


vector<double>
Accessibility::getAllAggregateAccessibilityVariables(
    float radius,
    string category,
    string aggtyp,
    string decay,
    int graphno) {
    if (accessibilityVars.find(category) == accessibilityVars.end() ||
        std::find(aggregations.begin(), aggregations.end(), aggtyp)
            == aggregations.end() ||
        std::find(decays.begin(), decays.end(), decay) == decays.end()) {
        // not found
        return vector<double>();
    }

    vector<double> scores(numnodes);

    #pragma omp parallel
    {
    #pragma omp for schedule(guided)
    for (int i = 0 ; i < numnodes ; i++) {
        scores[i] = aggregateAccessibilityVariable(
            i,
            radius,
            accessibilityVars[category],
            aggtyp,
            decay,
            graphno);
    }
    }
    return scores;
}


double
Accessibility::quantileAccessibilityVariable(
    DistanceVec &distances,
    accessibility_vars_t &vars,
    float quantile,
    float radius) {

    // first iterate through nodes in order to get count of items
    int cnt = 0;

    for (int i = 0 ; i < distances.size() ; i++) {
        int nodeid = distances[i].first;
        double distance = distances[i].second;

        if (distance > radius) continue;

        cnt += vars[nodeid].size();
    }

    if (cnt == 0) return -1;

    vector<float> vals(cnt);

    // make a second pass to put items in a single array for sorting
    for (int i = 0, cnt = 0 ; i < distances.size() ; i++) {
        int nodeid = distances[i].first;
        double distance = distances[i].second;

        if (distance > radius) continue;

        // and then iterate through all items at the node
        for (int j = 0 ; j < vars[nodeid].size() ; j++)
            vals[cnt++] = vars[nodeid][j];
    }

    std::sort(vals.begin(), vals.end());

    int ind = static_cast<int>(vals.size() * quantile);

    if (quantile <= 0.0) ind = 0;
    if (quantile >= 1.0) ind = vals.size()-1;

    return vals[ind];
}


double
Accessibility::aggregateAccessibilityVariable(
    int srcnode,
    float radius,
    accessibility_vars_t &vars,
    string aggtyp,
    string decay,
    int gno) {
    // I don't know if this is the best way to do this but I
    // I don't want to copy memory in the precompute case - sometimes
    // I need a reference and sometimes not
    DistanceVec tmp;
    DistanceVec &distances = tmp;
    if (dmsradius > 0 && radius <= dmsradius) {
        distances = dms[gno][srcnode];
    } else {
        ga[gno]->Range(
            srcnode,
            radius,
            omp_get_thread_num(),
            tmp);
    }

    if (distances.size() == 0) return -1;

    if (aggtyp == "min") {
        return this->quantileAccessibilityVariable(
            distances, vars, 0.0, radius);
    } else if (aggtyp == "25pct") {
        return this->quantileAccessibilityVariable(
            distances, vars, 0.25, radius);
    } else if (aggtyp == "median") {
        return this->quantileAccessibilityVariable(
            distances, vars, 0.5, radius);
    } else if (aggtyp == "75pct") {
        return this->quantileAccessibilityVariable(
            distances, vars, 0.75, radius);
    } else if (aggtyp == "max") {
        return this->quantileAccessibilityVariable(
            distances, vars, 1.0, radius);
    }

    if (aggtyp == "std") decay = "flat";

    int cnt = 0;
    double sum = 0.0;
    double sumsq = 0.0;

    std::function<double(const double &, const float &, const float &)> sum_function;

    if(decay == "exp")
        sum_function = [](const double &distance, const float &radius, const float &var)
                        { return exp(-1*distance/radius) * var; };
    if(decay == "linear")
        sum_function = [](const double &distance, const float &radius, const float &var)
                        { return (1.0-distance/radius) * var; };
    if(decay == "flat")
        sum_function = [](const double &distance, const float &radius, const float &var)
                        { return var; };

    for (int i = 0 ; i < distances.size() ; i++) {
        int nodeid = distances[i].first;
        double distance = distances[i].second;

        // this can now happen since we're precomputing
        if (distance > radius) continue;

        for (int j = 0 ; j < vars[nodeid].size() ; j++) {
            cnt++;  // count items
            sum += sum_function(distance, radius, vars[nodeid][j]);

            // stddev is always flat
            sumsq += vars[nodeid][j] * vars[nodeid][j];
        }
    }

    if (aggtyp == "count") return cnt;

    if (aggtyp == "mean" && cnt != 0) sum /= cnt;

    if (aggtyp == "std" && cnt != 0) {
        double mean = sum / cnt;
        return sqrt(sumsq / cnt - mean * mean);
    }

    return sum;
}

}  // namespace accessibility
}  // namespace MTC
