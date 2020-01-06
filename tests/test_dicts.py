import copy
import pickle
import unittest

from iarp_utils.dicts import DefaultOrderedDict, NotifyDict


class DictsTests(unittest.TestCase):

    def test_notify_dict_works(self):
        d = NotifyDict(test='blah', test2='here')
        self.assertEqual('blah', d['test'])
        d['test'] = 'here'
        self.assertIn('test', d.changed)
        self.assertNotIn('test2', d.changed)
        self.assertEqual(1, len(d.changed))
        self.assertEqual(2, len(d))

    def test_custom_ordered_dict(self):
        od = DefaultOrderedDict(dict)
        self.assertEqual("DefaultOrderedDict(<class 'dict'>, DefaultOrderedDict())", repr(od))
        od['single'] = 'here1'
        od['multiple']['levels'] = 'here2'
        self.assertIsNone(od.get('test'))
        self.assertEqual(od['single'], 'here1')
        self.assertEqual(od['multiple']['levels'], 'here2')

    def test_custom_ordered_dict_non_existing_key_returns_default_type(self):
        od = DefaultOrderedDict(dict)
        self.assertIsInstance(od['test'], (dict,))

    def test_custom_ordered_dict_raises_on_invalid_default_type(self):
        with self.assertRaises(TypeError):
            DefaultOrderedDict(True)

    def test_custom_ordered_dict_can_be_shallow_copied(self):
        od = DefaultOrderedDict(dict)
        od['single'] = 'here1'
        od['multiple']['levels'] = 'here2'
        tmp = copy.copy(od)
        self.assertIsNot(od, tmp)

        tmp = od.copy()
        self.assertNotEqual(id(od), id(tmp))

    def test_custom_ordered_dict_cannot_be_deep_copied(self):
        od = DefaultOrderedDict(dict)
        od['single'] = 'here1'
        od['multiple']['levels'] = 'here2'
        with self.assertRaises(NotImplementedError):
            copy.deepcopy(od)

    def test_pickling_dict(self):
        od = DefaultOrderedDict(dict)
        od['single'] = 'here1'
        od['multiple']['levels'] = 'here2'
        pickle.dumps(od)

    def test_pickle_dict_loads_correctly(self):
        od = DefaultOrderedDict(dict)
        od['single'] = 'here1'
        od['multiple']['levels'] = 'here2'
        p = pickle.dumps(od)

        nd = pickle.loads(p)
        self.assertIn('single', nd)
        self.assertEqual('here1', nd['single'])
        self.assertIn('multiple', nd)
        self.assertTrue(DefaultOrderedDict, type(nd['multiple']))
        self.assertIn('levels', nd['multiple'])
        self.assertEqual('here2', nd['multiple']['levels'])
        try:
            nd['another']['tree'] = True
        except KeyError:
            self.fail('DefaultOrderedDict not loaded from pickle correctly.')

