#include "accessibility.h"
#include <algorithm>
#include <cmath>
#include <utility>
#include "graphalg.h"

using std::vector;

namespace MTC {
namespace accessibility {

typedef std::pair<float, float> distance_node_pair;
bool distance_node_pair_comparator(const distance_node_pair& l,
                                   const distance_node_pair& r)
    { return l.first < r.first; }

Accessibility::Accessibility(int numnodes) {
    this->numnodes = numnodes;
    this->dmsradius = -1;
}


void Accessibility::addGraphalg(MTC::accessibility::Graphalg *g) {
    std::shared_ptr<MTC::accessibility::Graphalg>ptr(g);
    this->ga.push_back(ptr);
}


/*
#######################
POI QUERIES
#######################
*/

void Accessibility::initializePOIs(
    int numcategories,
    double maxdist,
    int maxitems) {
    // save this for when reinitializing the category
    this->maxdist = maxdist;
    this->maxitems = maxitems;
    // initialize for all subgraphs
    for (int i = 0 ; i < ga.size() ; i++) {
        ga[i]->initPOIs(numcategories, maxdist, maxitems);
    }
    accessibilityVarsForPOIs.resize(numcategories);
}


void Accessibility::initializeCategory(
    int category,
    vector<long> node_ids
    ) {
    accessibility_vars_t av;
    av.resize(this->numnodes);
    // initialize for all subgraphs
    for (int i = 0 ; i < ga.size() ; i++) {
        ga[i]->initPOIIndex(category, this->maxdist, this->maxitems);
        // initialize for each node
        for (int j = 0 ; j < node_ids.size() ; j++) {
            int node_id = node_ids[j];

            ga[i]->addPOIToIndex(category, node_id);
            assert(node_id << av.size());
            av[node_id].push_back(node_id);
        }
    }
    accessibilityVarsForPOIs[category] = av;
}


/* the return_nodeids parameter determines whether to
   return the nodeids where the poi was found rather than
   the distances - you can call this twice - once for the
   distances and then again for the node ids */
vector<double>
Accessibility::findNearestPOIs(
    int srcnode,
    float maxradius,
    unsigned number,
    unsigned cat,
    int gno,
    bool return_nodeids) {

    assert(cat >= 0 && cat < POI_MAXVAL);

    DistanceMap distances = ga[gno]->NearestPOI(cat, srcnode,
        maxradius, number, omp_get_thread_num());

    accessibility_vars_t &vars = accessibilityVarsForPOIs[cat];
    vector<distance_node_pair> distance_node_pairs;

    /* need to account for the possibility of having
       multiple locations at single node */
    for (DistanceMap::const_iterator itDist = distances.begin();
         itDist != distances.end();
         ++itDist) {
        int nodeid = itDist->first;
        double distance = itDist->second;

        for (int i = 0 ; i < vars[nodeid].size() ; i++) {
            distance_node_pairs.push_back(
               std::make_pair(
                   static_cast<double>(distance),
                   static_cast<double>(vars[nodeid][i])));
        }
    }

    std::sort(distance_node_pairs.begin(), distance_node_pairs.end(),
              distance_node_pair_comparator);

    vector<double> ret;
    for (unsigned i=0; i < distance_node_pairs.size(); i++) {
        ret.push_back(return_nodeids ?
                      distance_node_pairs[i].second :
                      distance_node_pairs[i].first);
    }

    return ret;
}


/* the return_nodeds param is described above */
vector<vector<double> >
Accessibility::findAllNearestPOIs(
    float maxradius,
    unsigned num_of_pois,
    unsigned category,
    int gno,
    bool return_nodeids) {
    vector<vector<double> >
        dists(numnodes, vector<double> (num_of_pois));

    #pragma omp parallel for
    for (int i = 0 ; i < numnodes ; i++) {
        vector<double> d = findNearestPOIs(
            i,
            maxradius,
            num_of_pois,
            category,
            gno,
            return_nodeids);
        for (int j = 0 ; j < num_of_pois ; j++) {
            if (j < d.size()) {
                dists[i][j] = d[j];
            } else {
                dists[i][j] = -1;
            }
        }
    }
    return dists;
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


/*
#######################
AGGREGATION/ACCESSIBILITY QUERIES
#######################
*/


void Accessibility::initializeAccVars(int numcategories) {
    accessibilityVars.resize(numcategories);
}


void Accessibility::initializeAccVar(
    int category,
    accessibility_vars_t &vars) {
    assert(vars.size() == numnodes);
    accessibilityVars[category] = vars;
}


vector<double>
Accessibility::getAllAggregateAccessibilityVariables(
    float radius,
    int ind,
    aggregation_types_t aggtyp,
    decay_func_t decay,
    int graphno) {

    if (ind == -1) assert(0);

    vector<double> scores(numnodes);

    #pragma omp parallel
    {
    #pragma omp for schedule(guided)
    for (int i = 0 ; i < numnodes ; i++) {
        scores[i] = aggregateAccessibilityVariable(
            i,
            radius,
            accessibilityVars[ind],
            aggtyp,
            decay,
            graphno);
    }
    }
    return scores;
}


DistanceVec
Accessibility::Range(int srcnode, float radius, int gno) {
    DistanceVec tmp;
    DistanceVec &distances = tmp;
    if (dmsradius > 0 && radius <= dmsradius) {
            distances = dms[gno][srcnode];
        return distances;
    } else {
        ga[gno]->Range(
            srcnode,
            radius,
            omp_get_thread_num(),
            tmp);
        return tmp;
    }
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

    if (aggtyp == AGG_MIN) {
        return this->quantileAccessibilityVariable(
            distances, vars, 0.0, radius);
    } else if (aggtyp == AGG_25PERCENTILE) {
        return this->quantileAccessibilityVariable(
            distances, vars, 0.25, radius);
    } else if (aggtyp == AGG_MEDIAN) {
        return this->quantileAccessibilityVariable(
            distances, vars, 0.5, radius);
    } else if (aggtyp == AGG_75PERCENTILE) {
        return this->quantileAccessibilityVariable(
            distances, vars, 0.75, radius);
    } else if (aggtyp == AGG_MAX) {
        return this->quantileAccessibilityVariable(
            distances, vars, 1.0, radius);
    }

    if (aggtyp == AGG_STDDEV) decay = DECAY_FLAT;

    int cnt = 0;
    double sum = 0.0;
    double sumsq = 0.0;

    for (int i = 0 ; i < distances.size() ; i++) {
        int nodeid = distances[i].first;
        double distance = distances[i].second;

        // this can now happen since we're precomputing
        if (distance > radius) continue;

        for (int j = 0 ; j < vars[nodeid].size() ; j++) {
            cnt++;  // count items

            if (decay == DECAY_EXP) {
                sum += exp(-1*distance/radius) * vars[nodeid][j];

            } else if (decay == DECAY_LINEAR) {
                sum += (1.0-distance/radius) * vars[nodeid][j];

            } else if (decay == DECAY_FLAT) {
                sum += vars[nodeid][j];

            } else {
                assert(0);
            }

            // stddev is always flat
            sumsq += vars[nodeid][j] * vars[nodeid][j];
        }
    }

    if (aggtyp == AGG_COUNT) return cnt;

    if (aggtyp == AGG_AVE && cnt != 0) sum /= cnt;

    if (aggtyp == AGG_STDDEV && cnt != 0) {
        double mean = sum / cnt;
        return sqrt(sumsq / cnt - mean * mean);
    }

    return sum;
}

}  // namespace accessibility
}  // namespace MTC
