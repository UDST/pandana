#pragma once
#ifdef WIN32
    #define DLLImport __declspec(dllimport)
    #define DLLExport __declspec(dllexport)
    #define DOTIMER 0
#else
    #define DLLImport
    #define DLLExport
    #define DOTIMER 0
#endif
#include <omp.h>
#define FILE_LOG(logINFO) (std::cout)
