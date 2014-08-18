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

#ifndef BASICDEFINITIONS_H_INCLUDED
#define BASICDEFINITIONS_H_INCLUDED

#ifdef max
#undef max
#endif

#include <climits>
#include <iostream>

using namespace std;

typedef unsigned int NodeID;
typedef unsigned int EdgeID;
typedef unsigned int EdgeWeight;
static const NodeID SPECIAL_NODEID = UINT_MAX;
static const EdgeID SPECIAL_EDGEID = UINT_MAX;

static const int LATLON_MULTIPLIER = 1000000;

#define INFO(x) do { std::cout << "[info " << __FILE__ << ":" << __LINE__ << "] " << x << std::endl; } while(0);
#define ERR(x) do { std::cerr << "[error " << __FILE__ << ":" << __LINE__ << "] " << x << std::endl; exit(-1); } while(0);
#define WARN(x) do { std::cerr << "[warn " << __FILE__ << ":" << __LINE__ << "] " << x << std::endl; } while(0);
#define CHDELETE(x) do { if(NULL != x) { delete x; x = NULL; } } while(0);
#define CHASSERT(x,y) do { if( !(x)) {ERR(y)} } while(0);


#endif // BASICDEFINITIONS_H_INCLUDED