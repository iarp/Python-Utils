import timeit
import cProfile


class Benchmark:
    """ Class that lets you quickly and easily calculate the time for something to run

    Examples:

        with Benchmark('join fn ln'):
            for x in range(1000000):
                a = ' '.join(['first', 'last name'])

        with Benchmark('format fn ln'):
            for x in range(1000000):
                a = '{} {}'.format('first', 'last name')

        with Benchmark('f-string fn ln'):
            first, last = 'first last name'.split(' ', 1)
            for x in range(1000000):
                a = f'{first} {last}'

    """
    class Break(Exception):
        """Allows breaking out of benchmark early"""

    def __init__(self, title='Benchmark', fmt="{:0.10}", end_message='\tbenchmark : {} : {} seconds'):
        print(f'Benchmarking {title}')
        self.msg = end_message.format(title, fmt)
        self.fmt = fmt

    def __enter__(self):
        self.start = timeit.default_timer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.time = timeit.default_timer() - self.start
        print(self.msg.format(self.time, time_raw=self.time))

        if exc_type == self.Break:
            return True


class Profiler:
    """ Class that lets you quickly and easily profile some code

    Examples:

        with Profiler():
            time.sleep(2)
    """
    def __init__(self, stats_sort='cumtime'):
        self.profile = cProfile.Profile()
        self.stats_sort = stats_sort

    def __enter__(self):
        self.profile.enable()
        return self

    def __exit__(self, *args, **kwargs):
        self.profile.disable()
        self.profile.print_stats(sort=self.stats_sort)
