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
 
 - A heap can be constructed without trowing an error
 - A heap is empty on construction
 - A queue has size 0 on construction
 - After n enqueues to an empty queue, n > 0, the queue is not empty and its size is n
 - If the size is n, then after n dequeues, the stack is empty and has a size 0
 - If one enqueues the values 1 through 50, in some random order, into an empty 
   queue, then if 50 dequeues are done the values dequeued are 1 through 50
   respectively
 - Dequeueing from an empty queue does throw an exception
 - Getting data from a non-existing element throws an exception
 */
#ifndef BINARYHEAP_TEST_H_INCLUDED
#define BINARYHEAP_TEST_H_INCLUDED

#include <algorithm>
#include <csignal>
#include "../../DataStructures/BinaryHeap.h"


typedef BinaryHeap< NodeID, NodeID, EdgeWeight, _HeapData, ArrayStorage<NodeID, NodeID>  > Heap;


BOOST_AUTO_TEST_SUITE(BinaryHeapTests)

BOOST_AUTO_TEST_CASE(ConstructingAndDestructing)
{
    try {
        Heap * heap = new Heap(100);
        delete heap;
    } catch (int e) {
        BOOST_REQUIRE(false);
    }
    BOOST_REQUIRE(true);
}

BOOST_AUTO_TEST_CASE(ConstructHeapAndUseIt)
{
    Heap heap(100);
    BOOST_REQUIRE(0 == heap.Size());
    //Insert(node, weight, parent);
    heap.Insert(0,10,100);
    BOOST_REQUIRE(1 == heap.Size());
    const NodeID min1 = heap.DeleteMin();
    BOOST_REQUIRE(0 == min1);
    const unsigned weight1 = heap.GetKey(min1);
    BOOST_REQUIRE( 10 == weight1);
    const unsigned parent1 = heap.GetData(min1).parent;
    BOOST_REQUIRE(100 == parent1);
}

BOOST_AUTO_TEST_CASE(SizeZeroOnConstruction)
{
    Heap heap(100);
    BOOST_REQUIRE(0 == heap.Size());
}

BOOST_AUTO_TEST_CASE(EmptyAfterNDequeues) {
    Heap heap(100);
    for(unsigned i = 0; i < 50; ++i)
        heap.Insert(i, i*2, 0);
    BOOST_REQUIRE(50 == heap.Size());
    for(unsigned i = 0; i < 50; ++i)
        heap.DeleteMin();
    BOOST_REQUIRE(0 == heap.Size());
}

BOOST_AUTO_TEST_CASE(OutPutIsSorted) {
    Heap heap(100);
    vector<unsigned> inputData;
    for(unsigned i = 50; i > 0; --i) {
        inputData.push_back(i-1);
    }
    std::random_shuffle(inputData.begin(), inputData.end());
    for(unsigned i = 0; i < 50; ++i) {
        heap.Insert(inputData[i], inputData[i], 0);
    }
    for(unsigned i = 0; i < 50; ++i) {
        BOOST_REQUIRE(i == heap.DeleteMin());
    }
    BOOST_REQUIRE(0 == heap.Size());
}

BOOST_AUTO_TEST_SUITE_END()
#endif
