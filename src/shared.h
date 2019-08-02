#pragma once
#ifdef _WIN32
    #define DLLImport __declspec(dllimport)
    #define DLLExport __declspec(dllexport)
#else
    #define DLLImport
    #define DLLExport
#endif
#ifdef _OPENMP
#include <omp.h>
#endif
#define FILE_LOG(logINFO) (std::cout)
