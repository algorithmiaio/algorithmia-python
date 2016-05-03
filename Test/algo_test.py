import sys
sys.path.append("../")

import unittest

import Algorithmia
import os

class AlgoTest(unittest.TestCase):
    def setUp(self):
        self.client = Algorithmia.client(os.environ['ALGORITHMIA_API_KEY'])

    def test_call_binary(self):
        result = self.client.algo('pmcq/Python2xEcho/0.1.0').pipe(bytearray('foo'))
        self.assertEquals('binary', result.metadata.content_type)
        self.assertEquals(bytearray('foo'), result.result)

if __name__ == '__main__':
    unittest.main()
