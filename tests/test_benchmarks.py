import os
import unittest

from iarp_utils.benchmarks import Benchmark, Profiler


class BenchmarkTests(unittest.TestCase):

    def test_benchmark_regular(self):
        with Benchmark('test'):
            pass

    def test_benchmark_breaker(self):
        with Benchmark('test'):
            raise Benchmark.Break


class ProfilerTests(unittest.TestCase):

    def test_profiler_regular(self):
        with Profiler():
            pass
