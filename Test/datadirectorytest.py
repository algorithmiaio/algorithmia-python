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

    def test_get_name(self):
        dd = DataDirectory(self.client, 'data://.my/this/is/a/long/path')
        self.assertEqual('path', dd.getName())

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

    def list_files_small(self, collectionName):
        dd = DataDirectory(self.client, collectionName)
        if (dd.exists()):
            dd.delete(True)

        dd.create()

        f1 = dd.file('a')
        f1.put('data')

        f2 = dd.file('b')
        f2.put('data')

        size = 0
        all_files = set()
        for f in dd.files():
            all_files.add(f.path)
            size += 1

        self.assertEqual(2, size)
        self.assertTrue('.my/test_list_files_small/a' in all_files)
        self.assertTrue('.my/test_list_files_small/b' in all_files)

        dd.delete(True)

    def test_list_files_small_without_trailing_slash(self):
        self.list_files_small('data://.my/test_list_files_small')

    def test_list_files_small_with_trailing_slash(self):
        self.list_files_small('data://.my/test_list_files_small/')

    def test_list_folders(self):
        dd = DataDirectory(self.client, 'data://.my/')

        dirName = '.my/test_list_directory'
        testDir = DataDirectory(self.client, 'data://' + dirName)
        if testDir.exists():
            testDir.delete(True)

        all_folders = set()
        for f in dd.dirs():
            all_folders.add(f.path)
        self.assertFalse(dirName in all_folders)

        testDir.create()
        all_folders = set()
        for f in dd.dirs():
            all_folders.add(f.path)
        self.assertTrue(dirName in all_folders)

        testDir.delete(True)

    def test_list_files_with_paging(self):
        NUM_FILES = 1100
        EXTENSION = '.txt'

        dd = DataDirectory(self.client, 'data://.my/pythonLargeDataDirList')
        if not dd.exists():
            dd.create()

            for i in range(NUM_FILES):
                dd.file(str(i) + EXTENSION).put(str(i))

        seenFiles = [False] * NUM_FILES
        numFiles = 0

        for f in dd.files():
            numFiles += 1
            name = f.getName()
            index = int(name[:-1 * len(EXTENSION)])
            seenFiles[index] = True

        allSeen = True
        for cur in seenFiles:
            allSeen = (allSeen and cur)

        self.assertEqual(NUM_FILES, numFiles)
        self.assertTrue(allSeen)

if __name__ == '__main__':
    unittest.main()
