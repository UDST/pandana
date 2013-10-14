/*
 open source routing machine
 Copyright (C) Dennis Luxen, others 2010
 
 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU AFFERO General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU Affero General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 or see http://www.gnu.org/licenses/agpl.txt.
 */

/*
 Here are some of the things we need to test:
 
 - Load data and Contract
 - Run simple queries with CH
 - Run simple queries with unidirectional Dijkstra
 - Add POIs
 - Query for POIs
 */
#ifndef LIBCH_TEST_H_INCLUDED
#define LIBCH_TEST_H_INCLUDED

#include <cassert>
#include <cstdlib>
#include <fstream>
#include <vector>

#include "../BasicDefinitions.h"
#include "../libch.h"

static const char * dataFile = "./src/UnitTests/data/berlin.osrm";

typedef std::map<NodeID, NodeID> ExternalNodeMap;

struct NodeInfo {
    int lat;
    int lon;
    NodeID id;
    NodeInfo(int ln, int lt, NodeID i) : lat(lt), lon(ln), id(i) {}
};

struct ImportEdge {
    bool operator< (const ImportEdge& e) const {
        if (source() == e.source()) {
            if (target() == e.target()) {
                if (weight() == e.weight()) {
                    return (isForward() && isBackward() &&
                            ((! e.isForward()) || (! e.isBackward())));
                }
                return (weight() < e.weight());
            }
            return (target() < e.target());
        }
        return (source() < e.source());
    }
    
    /** Default constructor. target and weight are set to 0.*/
    ImportEdge() :
    _source(0), _target(0), _name(0), _weight(0), forward(0), backward(0), _type(0) { assert(false); } //shall not be used.
    
    explicit ImportEdge(NodeID s, NodeID t, NodeID n, EdgeWeight w, bool f, bool b, short ty) :
    _source(s), _target(t), _name(n), _weight(w), forward(f), backward(b), _type(ty) { assert(ty >= 0); }
    
    NodeID target() const {return _target; }
    NodeID source() const {return _source; }
    NodeID name() const { return _name; }
    EdgeWeight weight() const {return _weight; }
    
    short type() const { assert(_type >= 0); return _type; }
    bool isBackward() const { return backward; }
    bool isForward() const { return forward; }
    bool isLocatable() const { return _type != 14; }
    
    NodeID _source;
    NodeID _target;
    NodeID _name:31;
    EdgeWeight _weight:31;
    bool forward:1;
    bool backward:1;
    short _type;
};

template<typename EdgeT>
NodeID readBinaryOSRMGraphFromStream(istream &in, vector<EdgeT>& edgeList, vector<NodeInfo> * int2ExtNodeMap) {
    NodeID n, source, target, id;
    EdgeID m;
    short dir;
    int xcoord, ycoord;// direction (0 = open, 1 = forward, 2+ = open)
    ExternalNodeMap ext2IntNodeMap;
    in.read((char*)&n, sizeof(NodeID));
    for (NodeID i=0; i<n;i++) {
        in.read((char*)&id, sizeof(unsigned));
        in.read((char*)&ycoord, sizeof(int));
        in.read((char*)&xcoord, sizeof(int));
        int2ExtNodeMap->push_back(NodeInfo(xcoord, ycoord, id));
        ext2IntNodeMap.insert(make_pair(id, i));
    }
    in.read((char*)&m, sizeof(unsigned));
    INFO("Importing n = " << n << " nodes ... and " << m << " edges ...");
    
    edgeList.reserve(m);
    for (EdgeID i=0; i<m; i++) {
        EdgeWeight weight;
        short type;
        NodeID nameID;
        int length;
        in.read((char*)&source, sizeof(unsigned));
        in.read((char*)&target, sizeof(unsigned));
        in.read((char*)&length, sizeof(int));
        in.read((char*)&dir,    sizeof(short));
        in.read((char*)&weight, sizeof(int));
        in.read((char*)&type,   sizeof(short));
        in.read((char*)&nameID ,sizeof(unsigned));
        
        assert(length > 0);
        assert(weight > 0);
        assert(0<=dir && dir<=2);
        
        bool forward = true;
        bool backward = true;
        if (1 == dir) { backward = false; }
        if (2 == dir) { forward = false; }
        
        BOOST_REQUIRE(length != 0);
        BOOST_REQUIRE(weight != 0);
        ExternalNodeMap::iterator intNodeID = ext2IntNodeMap.find(source);
        source = intNodeID->second;
        intNodeID = ext2IntNodeMap.find(target);
        BOOST_REQUIRE(ext2IntNodeMap.find(target) != ext2IntNodeMap.end());
        target = intNodeID->second;
        
        BOOST_REQUIRE(source != UINT_MAX && target != UINT_MAX);        
        EdgeT inputEdge(source, target, nameID, weight, forward, backward );
        edgeList.push_back(inputEdge);
    }
    ext2IntNodeMap.clear();
    vector<EdgeT>(edgeList.begin(), edgeList.end()).swap(edgeList); //remove excess candidates.
    return n;
}


BOOST_AUTO_TEST_SUITE(LibCHTest)
/*
BOOST_AUTO_TEST_CASE(LoadingAndContracting) {
    vector<NodeInfo> * int2ExtNodeMap = new vector<NodeInfo>();
    vector<CH::Edge> edgeList;
    
    //Load Graph
    ifstream in;
    in.open (dataFile, std::ifstream::in | std::ifstream::binary);
    BOOST_REQUIRE(in.is_open());
    const NodeID n = readBinaryOSRMGraphFromStream(in, edgeList, int2ExtNodeMap);
    in.close();
    
    //Build Hierarchy
    std::shared_ptr<CH::ContractionHierarchies> CHObject( new CH::ContractionHierarchies(2) );
    std::vector<CH::Node> nodeList;
    for(unsigned i = 0; i < n; ++i) {
        nodeList.push_back( CH::Node(i, 0, 0) );
    }
    CHObject->SetNodeVector(nodeList);
    CHObject->SetEdgeVector(edgeList);
    CHObject->RunPreprocessing();
}

BOOST_AUTO_TEST_CASE(LoadingAndContractingAndCHQueriesYieldSameDistance) {
    vector<NodeInfo> * int2ExtNodeMap = new vector<NodeInfo>();
    vector<CH::Edge> edgeList;
    
    //Load Graph
    ifstream in;
    in.open (dataFile , std::ifstream::in | std::ifstream::binary);
    BOOST_REQUIRE(in.is_open());
    const NodeID n = readBinaryOSRMGraphFromStream(in, edgeList, int2ExtNodeMap);
    in.close();
    
    //Build Hierarchy
    std::shared_ptr<CH::ContractionHierarchies> CHObject( new CH::ContractionHierarchies(2) );
    std::vector<CH::Node> nodeList;
    for(unsigned i = 0; i < n; ++i) {
        nodeList.push_back( CH::Node(i, 0, 0) );
    }
    CHObject->SetNodeVector(nodeList);
    CHObject->SetEdgeVector(edgeList);
    CHObject->RunPreprocessing();
    
    //Run Queries and compare with result of unidirectional Dijkstra
    std::vector<NodeID> resultingPath;
    int dist1 = CHObject->computeLengthofShortestPath(CH::Node(0,0,0), CH::Node(n-n/2, 0, 0));
    int dist2 = CHObject->computeShortestPath(CH::Node(0,0,0), CH::Node(n-n/2, 0, 0), resultingPath);
    int dijkstraDist1 = CHObject->computeVerificationLengthofShortestPath(CH::Node(0,0,0), CH::Node(n-n/2, 0, 0));
    BOOST_REQUIRE_EQUAL( dist1, dist2);
    BOOST_REQUIRE_EQUAL( dist1, dijkstraDist1);
    BOOST_REQUIRE(0 != resultingPath.size());
    resultingPath.clear();
    dist1 = CHObject->computeLengthofShortestPath(CH::Node(1,0,0), CH::Node(n-n/2-1, 0, 0));
    dist2 = CHObject->computeShortestPath(CH::Node(1,0,0), CH::Node(n-n/2-1, 0, 0), resultingPath);
    dijkstraDist1 = CHObject->computeVerificationLengthofShortestPath(CH::Node(1,0,0), CH::Node(n-n/2-1, 0, 0));
    BOOST_REQUIRE_EQUAL( dist1, dist2);
    BOOST_REQUIRE_EQUAL( dist1, dijkstraDist1);
    BOOST_REQUIRE(0 != resultingPath.size());
    
}

BOOST_AUTO_TEST_CASE(LoadingAndContractingAndAddingRandomPOIs) {
    vector<NodeInfo> * int2ExtNodeMap = new vector<NodeInfo>();
    vector<CH::Edge> edgeList;
    
    //Load Graph
    ifstream in;
    in.open (dataFile, std::ifstream::in | std::ifstream::binary);
    BOOST_REQUIRE(in.is_open());
    const NodeID n = readBinaryOSRMGraphFromStream(in, edgeList, int2ExtNodeMap);
    in.close();
    
    //Build Hierarchy
    std::shared_ptr<CH::ContractionHierarchies> CHObject( new CH::ContractionHierarchies(2) );
    std::vector<CH::Node> nodeList;
    for(unsigned i = 0; i < n; ++i) {
        nodeList.push_back( CH::Node(i, 0, 0) );
    }
    CHObject->SetNodeVector(nodeList);
    CHObject->SetEdgeVector(edgeList);
    CHObject->RunPreprocessing();
    
    //Generate list of 10 random POIs
    srand ( 37773);
    std::vector<NodeID> POIs;
    for(unsigned i = 0; i < 10; ++i)
        POIs.push_back(rand() % n + 1);
    
    CHObject->createPOIIndexArray(1, 1500, 3);
    for(unsigned i = 0; i < 10; ++i)
        CHObject->addPOIToIndex(0, POIs[i]);
}*/

BOOST_AUTO_TEST_CASE(LoadingAndContractingAndAddingRandomPOIsANdQueryThem) {
    vector<NodeInfo> * int2ExtNodeMap = new vector<NodeInfo>();
    vector<CH::Edge> edgeList;
    
    //Load Graph
    ifstream in;
    in.open (dataFile, std::ifstream::in | std::ifstream::binary);
    BOOST_REQUIRE(in.is_open());
    const NodeID n = readBinaryOSRMGraphFromStream(in, edgeList, int2ExtNodeMap);
    in.close();
    
    //Build Hierarchy
    std::shared_ptr<CH::ContractionHierarchies> CHObject( new CH::ContractionHierarchies(2) );
    std::vector<CH::Node> nodeList;
    for(unsigned i = 0; i < n; ++i) {
        nodeList.push_back( CH::Node(i, 0, 0) );
    }
    CHObject->SetNodeVector(nodeList);
    CHObject->SetEdgeVector(edgeList);
    CHObject->RunPreprocessing();
    
    //Generate list of 10 random POIs
    srand ( 37773);
    std::vector<NodeID> POIs;
    for(unsigned i = 0; i < 10; ++i)
        POIs.push_back(rand() % n + 1);
    
    CHObject->createPOIIndexArray(1, 1500, 3);
    for(unsigned i = 0; i < 10; ++i)
        CHObject->addPOIToIndex(0, POIs[i]);
    
    std::vector<CH::BucketEntry> resultingPOIs;
    for(unsigned i = 0; i < 10; ++i) {    
        CHObject->getNearest(0, POIs[i], resultingPOIs);
        BOOST_REQUIRE(0 != resultingPOIs.size());
        BOOST_REQUIRE_EQUAL(resultingPOIs[0].distance, 0);
        BOOST_REQUIRE_EQUAL(resultingPOIs[0].node, POIs[i]);
        INFO("POI #" << i << " = " << resultingPOIs.size());
        resultingPOIs.clear();
    }
}

BOOST_AUTO_TEST_SUITE_END()

#endif //LIBCH_TEST_H_INCLUDED
