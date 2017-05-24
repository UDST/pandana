#pragma once

#include <vector>
#include <map>
#include <utility>
#include "./shared.h"
#include "./contraction_hierarchies/src/libch.h"

typedef unsigned int NodeID;

#define DISTANCEMULTFACT 1000.0

namespace MTC {
namespace accessibility {

typedef std::map<int, float> DistanceMap;
typedef std::vector<std::pair<NodeID, float> > DistanceVec;

class Graphalg {
 public:
    Graphalg(
        int *nodeids, float *nodexy, int numnodes,
        int *edges, float *edgeweights, int numedges,
        bool twoway);

    std::vector<NodeID> Route(int src, int tgt, int threadNum = 0);

    double Distance(int src, int tgt, int threadNum = 0);

    void Range(int src, double maxdist, int threadNum,
               DistanceVec &ResultingNodes);

    DistanceMap NearestPOI(
        int category, int src, double maxdist,
        int number, int threadNum = 0);

    void initPOIs(int numcategories, double maxdist, int maxitems) {
        ch.createPOIIndexArray(numcategories, maxdist*DISTANCEMULTFACT,
                               maxitems);
    }

    void addPOIToIndex(int category, int i) {
        ch.addPOIToIndex(category, i);
    }

    int numnodes;
    CH::ContractionHierarchies ch;
};
}  // namespace accessibility
}  // namespace MTC
