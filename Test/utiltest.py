import sys
sys.path.append("../")

import unittest

import Algorithmia
from Algorithmia.util import getParentAndBase, pathJoin

class UtilTest(unittest.TestCase):
    def test_getParentAndBase(self):
        self.assertEqual(('a/b', 'c'), getParentAndBase('a/b/c'))
        self.assertEqual(('a/b', 'c'), getParentAndBase('a/b/c///'))
        self.assertEqual(('//a//b', 'c'), getParentAndBase('//a//b////c///'))

    def test_getParentAndBase_errors(self):
        self.assertRaises(Exception, getParentAndBase, '/')
        self.assertRaises(Exception, getParentAndBase, '')
        self.assertRaises(Exception, getParentAndBase, 'a/')

    def test_pathJoin(self):
        self.assertEqual('/a/b/c/d', pathJoin('/a/b/c/', 'd'))
        self.assertEqual('/a/b/c/d', pathJoin('/a/b/c', 'd'))
        self.assertEqual('/a//b/c///d', pathJoin('/a//b/c//', '/d'))

if __name__ == '__main__':
    unittest.main()