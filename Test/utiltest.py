import sys
sys.path.append("../")

import unittest

import Algorithmia
from Algorithmia.util import getParentAndBase

class UtilTest(unittest.TestCase):
    def test_getParentAndBase(self):
        self.assertEqual(('a/b', 'c'), getParentAndBase('a/b/c'))
        self.assertEqual(('a/b', 'c'), getParentAndBase('a/b/c///'))
        self.assertEqual(('//a//b', 'c'), getParentAndBase('//a//b////c///'))

    def test_getParentAndBase_errors(self):
        self.assertRaises(Exception, getParentAndBase, '/')
        self.assertRaises(Exception, getParentAndBase, '')
        self.assertRaises(Exception, getParentAndBase, 'a/')

if __name__ == '__main__':
    unittest.main()