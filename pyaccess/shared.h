#pragma once
#ifdef LINUX
#define DLLImport
#define DLLExport 
#define DOTIMER 0
#else
#define DLLImport __declspec(dllimport)
#define DLLExport __declspec(dllexport)
#define DOTIMER 0
#endif
#define FILE_LOG(logINFO) (std::cout)
