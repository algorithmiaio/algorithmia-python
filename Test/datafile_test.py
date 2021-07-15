import sys

# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest, os, uuid
import numpy as np
import Algorithmia
import json
from Algorithmia.datafile import DataFile, LocalDataFile, AdvancedDatafile

class DataFileTest(unittest.TestCase):
    def setUp(self):
        self.client = Algorithmia.client()
        if not self.client.dir("data://.my/empty").exists():
            self.client.dir("data://.my/empty").create()

    def test_get_nonexistant(self):
        df = self.client.file('data://.my/nonexistant/nonreal')
        try:
            df.getFile()
            retrieved_file = True
        except Exception as e:
            retrieved_file = False
        self.assertFalse(retrieved_file)

    def test_get_str(self):
        df = self.client.file('data://.my/nonexistant/nonreal')
        try:
            print(df.getString())
            retrieved_file = True
        except Exception as e:
            retrieved_file = False
        self.assertFalse(retrieved_file)

    def test_set_attributes(self):
        df = DataFile(self.client, 'data://.my/empty')

        try:
            df.set_attributes({
                'last_modified': '2019-01-09T22:44:31.632Z',
                'size': 0
            })
        except Exception as e:
            self.fail("set_attributes failed with exception: " + str(e))

    def test_putJson_getJson(self):
        file = '.my/empty/test.json'
        df = DataFile(self.client,'data://'+file)
        if sys.version_info[0] < 3:
            payload = {u"hello":u"world"}
        else:
            payload = {"hello": "world"}
        response = df.putJson(payload)
        self.assertEqual(response.path,file)
        result = self.client.file(file).getJson()
        self.assertEqual(str(result), str(payload))

    def test_putNumpy_getNumpy(self):
        file = ".my/empty/numpy.json"
        df = DataFile(self.client, 'data://' + file)
        arr = np.array([0, 0, 0, 0], dtype=np.int64)
        response = df.putNumpy(arr)
        self.assertEqual(response.path, file)
        result = self.client.file(file).getNumpy()
        self.assertEqual(str(arr), str(result))

        
class LocalFileTest(unittest.TestCase):
    DUMMY_TEXT = 'this file gets populated during testing'
    EXISTING_TEXT = 'this file exists before testing'
    def setUp(self):
        self.client = Algorithmia.client()
        # Make a file that DOES exist and has contents,
        self.EXISTING_FILE = 'file://'+str(uuid.uuid1())+'.txt'
        f = open(self.EXISTING_FILE.replace('file://', ''), 'w')
        f.write(self.EXISTING_TEXT)
        f.close()
        # We need a dummy file that doesnt currently exist
        self.DUMMY_FILE = 'file://'+str(uuid.uuid1())+'.txt'
        if os.path.isfile(self.DUMMY_FILE): os.remove(self.DUMMY_FILE)
    def tearDown(self):
        os.remove(self.EXISTING_FILE.replace('file://', ''))
        if os.path.isfile(self.DUMMY_FILE): os.remove(self.DUMMY_FILE.replace('file://', ''))
    def test_local_remote(self):
        self.assertTrue(isinstance(self.client.file(self.DUMMY_FILE), LocalDataFile))
        self.assertTrue(isinstance(self.client.file('data://foo'), DataFile))
    def test_exists_or_not(self):
        self.assertTrue(self.client.file(self.EXISTING_FILE).exists())
        self.assertFalse(self.client.file(self.DUMMY_FILE).exists())
    def test_get_nonexistant(self):
        df = self.client.file(self.DUMMY_FILE)
        try:
            df.getFile()
            retrieved_file = True
        except Exception as e:
            retrieved_file = False
        self.assertFalse(retrieved_file)
    def test_put_and_read_and_delete(self):
        f = self.client.file(self.DUMMY_FILE)
        f.put(self.DUMMY_TEXT)
        # Check getString
        txt = self.client.file(self.DUMMY_FILE).getString()
        self.assertEqual(txt, self.DUMMY_TEXT)
        # Check delete
        deletion_status = self.client.file(self.DUMMY_FILE).delete()
        self.assertTrue(deletion_status)
    def test_read_types(self):
        # Check getBytes
        txt = self.client.file(self.EXISTING_FILE).getBytes().decode('utf-8')
        self.assertEqual(txt, self.EXISTING_TEXT)
        # Check getFile
        txt = self.client.file(self.EXISTING_FILE).getFile().read()
        self.assertEqual(txt, self.EXISTING_TEXT)

class AdvancedDataFileTest(unittest.TestCase):
    def setUp(self):
        self.client = Algorithmia.client()
        if not self.client.dir("data://.my/empty").exists():
            self.client.dir("data://.my/empty").create()

    def test_get_nonexistant(self):
        try:
            with self.client.file('data://.my/nonexistant/nonreal', advanced=True) as f:
                _ = f.read()
            retrieved_file = True
        except Exception as e:
            retrieved_file = False
        self.assertFalse(retrieved_file)

    def test_get_str(self):
        df = self.client.file('data://.my/nonexistant/nonreal', advanced=True)
        try:
            print(df.getString())
            retrieved_file = True
        except Exception as e:
            retrieved_file = False
        self.assertFalse(retrieved_file)

    def test_putJson_getJson(self):
        file = '.my/empty/test.json'
        df = AdvancedDatafile(self.client,'data://'+file, cleanup=True)
        if sys.version_info[0] < 3:
            payload = {u"hello":u"world"}
        else:
            payload = {"hello": "world"}
        response = df.putJson(payload)
        self.assertEqual(response.path,file)
        result = json.loads(df.read())
        self.assertDictEqual(result, payload)
        self.assertEqual(str(result), str(payload))

if __name__ == '__main__':
    unittest.main()
