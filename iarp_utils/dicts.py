from collections import OrderedDict, Callable


class NotifyDict(dict):
    """ Keep track of changes to a dict after initial creation.

    Examples:

        >>> d = NotifyDict(test1='here', test2='here2')
        >>> d['test1'] = 'changed'
        >>> d.changed
        {'test1'}
        >>> d.changed.clear()
        >>> d.changed
        {}

    """
    changed = set()

    def __setitem__(self, key, value):
        self.changed.add(key)
        dict.__setitem__(self, key, value)


class DefaultOrderedDict(OrderedDict):
    """Combines DefaultDict and OrderedDict into one.
    Source: http://stackoverflow.com/a/6190500/562769

    Examples:

        >>> dod = DefaultOrderedDict(dict)
        >>> dod['many']['levels']['deep'] = True
        # will not throw KeyErrors about many not existing.
    """
    def __init__(self, default_factory, *a, **kw):
        if not isinstance(default_factory, Callable):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        return OrderedDict.__getitem__(self, key)

    def __missing__(self, key):
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()  # pragma: no cover
        else:
            args = self.default_factory,
        return type(self), args, None, None, iter(self.items())

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        raise NotImplementedError('deepcopy not permitted on DefaultOrderedDict.')

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory, OrderedDict.__repr__(self))
