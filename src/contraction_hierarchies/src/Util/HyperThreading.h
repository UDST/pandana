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
#ifndef HYPERTHREADING_H_INCLUDED
#define HYPERTHREADING_H_INCLUDED

inline void cpuID(unsigned i, unsigned regs[4]) {
#ifdef _WIN32
    //__cpuid((int *)regs, (int)i);
    
#else
    asm volatile
    ("cpuid" : "=a" (regs[0]), "=b" (regs[1]), "=c" (regs[2]), "=d" (regs[3])
     : "a" (i), "c" (0));
    // ECX is set to zero for CPUID function 4
#endif
}

inline int getNumberOfRealCPUs () {
    unsigned regs[4];
    
    // Get vendor
    char vendor[12];
    cpuID(0, regs);
    ((unsigned *)vendor)[0] = regs[1]; // EBX
    ((unsigned *)vendor)[1] = regs[3]; // EDX
    ((unsigned *)vendor)[2] = regs[2]; // ECX
    string cpuVendor = string(vendor, 12);
    
    // Get CPU features
    cpuID(1, regs);
    unsigned cpuFeatures = regs[3]; // EDX
    
    // Detect hyper-threads  
    bool hyperThreads = false;
    if (cpuVendor == "GenuineIntel" && cpuFeatures & (1 << 28)) { // HTT bit
        // Logical core count per CPU
        cpuID(1, regs);
        unsigned logical = (regs[1] >> 16) & 0xff; // EBX[23:16]
        cout << " logical cpus: " << logical << endl;
        unsigned cores = logical;
        
        if (cpuVendor == "GenuineIntel") {
            // Get DCP cache info
            cpuID(4, regs);
            cores = ((regs[0] >> 26) & 0x3f) + 1; // EAX[31:26] + 1
            
        } else if (cpuVendor == "AuthenticAMD") {
            // Get NC: Number of CPU cores - 1
            cpuID(0x80000008, regs);
            cores = ((unsigned)(regs[2] & 0xff)) + 1; // ECX[7:0] + 1
        }
        
        cout << "    cpu cores: " << cores << endl;
        
        if (cores < logical) hyperThreads = true;
        return cores;
    }
    
    cout << "hyper-threads: " << (hyperThreads ? "true" : "false") << endl;
    return 1;
}

#endif
