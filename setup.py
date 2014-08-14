from setuptools import setup, Extension
import numpy as np

extension_name = '_pyaccess'
extension_version = '0.1dev'

include_dirs = [
    'ann_1.1.2/include',
    'sparsehash-2.0.2/src',
    np.get_include(),
    '.'
]
library_dirs = [
    'ann_1.1.2/lib',
    'contraction_hierarchies'
]
packages = ['pyaccess']
libraries = ['ANN', 'ch', 'gomp']
source_files = [
    'pyaccess/accessibility.cpp',
    'pyaccess/graphalg.cpp',
    'pyaccess/nearestneighbor.cpp',
    'pyaccess/pyaccesswrap.cpp'
]
extra_compile_args = [
    '-shared',
    '-DMACOSX',
    '-DLINUX',
    '-w',
    '-std=gnu++0x',
    '-O3',
    '-fopenmp',
    '-fpic',
    '-g',
    '-Wno-deprecated',
]

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
