#pragma once
#ifdef _WIN32
    #define DLLImport __declspec(dllimport)
    #define DLLExport __declspec(dllexport)
#else
    #define DLLImport
    #define DLLExport
#endif
#include <stdint.h>
#ifdef _OPENMP
#include <omp.h>
#else
#define PANDANA_OMP_FALLBACK
#define omp_get_thread_num() 0
#define omp_get_max_threads() 1
#endif
#define FILE_LOG(logINFO) (std::cout)

// External (OSM or user) node IDs stay 64-bit. Internal graph indices are
// dense positions 0..numnodes-1 and use int.
typedef int64_t PandanaExternalNodeID;
