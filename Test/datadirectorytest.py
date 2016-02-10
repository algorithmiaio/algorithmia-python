import sys
sys.path.append("../")

import unittest

import Algorithmia
from Algorithmia import client
from Algorithmia.datadirectory import DataDirectory
import os

class DataDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.client = client(os.environ['ALGORITHMIA_API_KEY'])

    def test_directory_does_not_exit(self):
        dd = DataDirectory(self.client, "data://.my/this_should_never_be_created")
        self.assertFalse(dd.exists())

    def test_empty_directory_creation_and_deletion(self):
        dd = DataDirectory(self.client, "data://.my/empty_test_directory")

        if (dd.exists()):
            dd.delete(False)

        self.assertFalse(dd.exists())

        dd.create()
        self.assertTrue(dd.exists())

        # get rid of it
        dd.delete(False)
        self.assertFalse(dd.exists())

    def test_nonempty_directory_creation_and_deletion(self):
        dd = DataDirectory(self.client, "data://.my/nonempty_test_directory")

        if (dd.exists()):
            dd.delete(True)

        self.assertFalse(dd.exists())

        dd.create()
        self.assertTrue(dd.exists())

        f = dd.file('one')
        self.assertFalse(f.exists())
        f.put('data')
        self.assertTrue(f.exists())

        # Try deleting without the force - the directory should still be there
        self.assertRaises(Exception, dd.delete)
        self.assertTrue(dd.exists())
        self.assertTrue(f.exists())

        dd.delete(True)
        self.assertFalse(dd.exists())
        self.assertFalse(f.exists())


if __name__ == '__main__':
    unittest.main()
