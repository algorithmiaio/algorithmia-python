import sys
# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest

from Algorithmia.__main__ import CLI

class AlgoTest(unittest.TestCase):
    def setUp(self):
        self.client = Algorithmia.client()

    def test_call_binary(self):
        result = self.client.algo('util/Echo').pipe(bytearray('foo','utf-8'))
        self.assertEquals('binary', result.metadata.content_type)
        self.assertEquals(bytearray('foo','utf-8'), result.result)

    def test_text_unicode(self):
        telephone = u"\u260E"

        #Unicode input to pipe()
        result1 = self.client.algo('util/Echo').pipe(telephone)
        self.assertEquals('text', result1.metadata.content_type)
        self.assertEquals(telephone, result1.result)

        #Unicode return in .result
        result2 = self.client.algo('util/Echo').pipe(result1.result)
        self.assertEquals('text', result2.metadata.content_type)
        self.assertEquals(telephone, result2.result)

    # def test_json_unicode(self):
    #     telephone = [u"\u260E"]
    #
    #     #Unicode input to pipe()
    #     result1 = self.client.algo('util/Echo').pipe(telephone)
    #     self.assertEquals('json', result1.metadata.content_type)
    #     self.assertEquals(telephone, result1.result)
    #
    #     #Unicode return in .result
    #     result2 = self.client.algo('util/Echo').pipe(result1.result)
    #     self.assertEquals('json', result2.metadata.content_type)
    #     self.assertEquals(telephone, result2.result)

if __name__ == '__main__':
    unittest.main()
