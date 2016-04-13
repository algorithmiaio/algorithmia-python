import sys
sys.path.append("../")

import unittest

import Algorithmia
import os

class DataDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.client = Algorithmia.client(os.environ['ALGORITHMIA_API_KEY'])

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
            print df.getString()
            retrieved_file = True
        except Exception as e:
            retrieved_file = False
        self.assertFalse(retrieved_file)

if __name__ == '__main__':
    unittest.main()