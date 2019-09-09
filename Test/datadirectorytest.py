import sys
# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest
import os

import Algorithmia
from Algorithmia.datadirectory import DataDirectory, LocalDataDirectory
from Algorithmia.data import DataObjectType
from Algorithmia.acl import Acl, AclType

class DataDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.client = Algorithmia.client()

    def test_get_name(self):
        dd = DataDirectory(self.client, 'data://.my/this/is/a/long/path')
        self.assertEqual('path', dd.getName())

    def test_directory_does_not_exit(self):
        dd = DataDirectory(self.client, "data://.my/this_should_never_be_created")
        self.assertFalse(dd.exists())

    def test_alternate_directory_syntax(self):
        # Check alternate dir syntax
        dd = self.client.dir("data://.my/this_should_never_be_created")
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

    def test_data_object(self):
        dd = DataDirectory(self.client, 'data://foo')
        self.assertTrue(dd.is_dir())
        self.assertFalse(dd.is_file())
        self.assertTrue(dd.get_type() is DataObjectType.directory)

class LocalDataDirectoryTest(unittest.TestCase):
    _DUMMY_DIR = 'dummy_dir_that_should_not_exist'
    _EXISTING_DIR = 'existing_dir_that_should_not_exist_before_test'
    EXISTING_FILES = ['file1.txt', 'file2.txt']
    def setUp(self):
        self.client = Algorithmia.client()
        self.DUMMY_DIR = 'file://' + self._DUMMY_DIR
        self.EXISTING_DIR = 'file://' + self._EXISTING_DIR
        # create existing dir w files in it
        os.mkdir(self._EXISTING_DIR)
        for fname in self.EXISTING_FILES:
            with open(self._EXISTING_DIR+'/'+fname, 'w') as f:
                f.write('filler text')
        # ensure dummy dir does not exist yet
        assert not os.path.isdir(self.DUMMY_DIR)
    def tearDown(self):
        for fname in self.EXISTING_FILES:
            os.remove(self._EXISTING_DIR+'/'+fname)
        os.rmdir(self._EXISTING_DIR)
    def test_exist_or_not(self):
        self.assertTrue(self.client.dir(self.EXISTING_DIR).exists())
        self.assertFalse(self.client.dir(self.DUMMY_DIR).exists())
    def test_create_delete(self):
        self.client.dir(self.DUMMY_DIR).create()
        self.assertTrue(self.client.dir(self.DUMMY_DIR).exists())
        self.client.dir(self.DUMMY_DIR).delete()
        self.assertFalse(self.client.dir(self.DUMMY_DIR).exists())
    def test_list(self):
        contents = set(x for x in self.client.dir(self.EXISTING_DIR).list())
        self.assertEqual(contents, set(self.EXISTING_FILES))


if __name__ == '__main__':
    unittest.main()
