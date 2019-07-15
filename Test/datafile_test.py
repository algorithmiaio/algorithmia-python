import sys
sys.path.append("../")

import unittest

import Algorithmia
from Algorithmia.datafile import DataFile

class DataDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.client = Algorithmia.client()

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

if __name__ == '__main__':
    unittest.main()
