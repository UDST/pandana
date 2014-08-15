from setuptools import setup, Extension
import numpy as np

OPENMP = False

extension_name = '_pyaccess'
extension_version = '0.1dev'

include_dirs = [
    np.get_include(),
    '.'
]
library_dirs = [
]
packages = ['pyaccess']
libraries = []
source_files = [
    'pyaccess/accessibility.cpp',
    'pyaccess/graphalg.cpp',
    'pyaccess/nearestneighbor.cpp',
    'pyaccess/pyaccesswrap.cpp',
    'contraction_hierarchies/src/libch.cpp',
    'ann_1.1.2/src/ANN.cpp',
    'ann_1.1.2/src/brute.cpp',
    'ann_1.1.2/src/kd_tree.cpp',
    'ann_1.1.2/src/kd_util.cpp',
    'ann_1.1.2/src/kd_split.cpp',
    'ann_1.1.2/src/kd_dump.cpp',
    'ann_1.1.2/src/kd_search.cpp',
    'ann_1.1.2/src/kd_pr_search.cpp',
    'ann_1.1.2/src/kd_fix_rad_search.cpp',
    'ann_1.1.2/src/bd_tree.cpp',
    'ann_1.1.2/src/bd_search.cpp',
    'ann_1.1.2/src/bd_pr_search.cpp',
    'ann_1.1.2/src/bd_fix_rad_search.cpp',
    'ann_1.1.2/src/perf.cpp'
]
extra_compile_args = [
    '-shared',
    '-DMACOSX',
    '-DLINUX',
    '-w',
    '-std=c++0x',
    '-O3',
    '-fpic',
    '-g',
    '-static',
    '-Wno-deprecated',
    '-Iann_1.1.2/include'
    #'-stdlib=libc++'
]
if OPENMP:
    extra_compile_args += ['-DOPENMP', '-fopenmp']

py_modules = ['pyaccess/pyaccess', 'pyaccess/urbanaccess']

setup(
    packages=packages,
    py_modules=py_modules,
    name='pyaccess',
    version=extension_version,
    ext_modules=[
        Extension(
            extension_name,
            source_files,
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            libraries=libraries,
            extra_compile_args=extra_compile_args
        )
    ]
)
