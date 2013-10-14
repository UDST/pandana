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

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE Basic Contraction Hierarchies Tests

#include <boost/test/unit_test.hpp>
#include "../BasicDefinitions.h"
#include "libch_test.h"
#include "DataStructures/BinaryHeap_Test.h"

BOOST_AUTO_TEST_SUITE(Trivial)

BOOST_AUTO_TEST_CASE(TrivialTestCase1)
{
	float x = 9.5f;
    
	BOOST_CHECK(x != 0.0f);
	BOOST_CHECK_EQUAL((int)x, 9);
	BOOST_CHECK_CLOSE(x, 9.5f, 0.0001f); // Checks differ no more then 0.0001%
}

BOOST_AUTO_TEST_SUITE_END()