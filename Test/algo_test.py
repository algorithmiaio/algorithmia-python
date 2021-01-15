import sys
import os
from Algorithmia.errors import AlgorithmException
# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest

import Algorithmia

class AlgoTest(unittest.TestCase):
    def setUp(self):
        self.client = Algorithmia.client()

    def test_call_customCert(self):
        open("./test.pem",'w')
        c = Algorithmia.client(ca_cert="./test.pem")
        result = c.algo('util/Echo').pipe(bytearray('foo','utf-8'))
        self.assertEquals('binary', result.metadata.content_type)
        self.assertEquals(bytearray('foo','utf-8'), result.result)
        try:
            os.remove("./test.pem")
        except OSError as e:
            print(e)
        
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

    def test_get_build_by_id(self):
        result = self.client.algo("J_bragg/Echo").get_build("1a392e2c-b09f-4bae-a616-56c0830ac8e5")
        self.assertTrue(result.build_id is not None)

    def test_get_build_logs(self):
        result = self.client.algo("J_bragg/Echo").get_build_logs("1a392e2c-b09f-4bae-a616-56c0830ac8e5")
        self.assertTrue(result.logs is not None)

    def test_get_scm_status(self):
        result = self.client.algo("J_bragg/Echo").get_scm_status()
        self.assertTrue(result.scm_connection_status is not None)

    def test_exception_ipa_algo(self):
        try:
            result = self.client.algo('zeryx/raise_exception').pipe("")
        except AlgorithmException as e:
            self.assertEqual(e.message, "This is an exception")

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
