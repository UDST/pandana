"""Check that an installed Pandana build is using OpenMP multithreading.

Runs examples/simple_example.py in a subprocess and parses the thread count
that the C++ code logs while building the contraction hierarchy. Exits
non-zero if fewer than two threads were used. The wheel-building workflow
runs this so that a silently single-threaded wheel fails CI.

Usage: python tests/check_openmp.py [min_threads]
"""
import os
import re
import subprocess
import sys

min_threads = int(sys.argv[1]) if len(sys.argv) > 1 else 2

here = os.path.dirname(os.path.abspath(__file__))
example = os.path.join(here, os.pardir, "examples", "simple_example.py")

result = subprocess.run(
    [sys.executable, example], capture_output=True, text=True, check=True)
output = result.stdout + result.stderr

match = re.search(r"contraction hierarchies with (\d+) threads", output)
if not match:
    sys.exit("Could not find the thread count in the demo output:\n" + output)

threads = int(match.group(1))
print("Pandana built the contraction hierarchies with {} threads".format(
    threads))
if threads < min_threads:
    sys.exit("Expected at least {} threads; OpenMP is not working".format(
        min_threads))
