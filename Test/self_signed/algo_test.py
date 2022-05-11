import sys
import os
from Algorithmia.errors import AlgorithmException
from Algorithmia.algorithm import OutputType
import Algorithmia

# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest

if sys.version_info.major >= 3:

    class AlgoDummyTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.client = Algorithmia.client(api_address="https://localhost:8090", api_key="simabcd123", ca_cert=False)

        def test_call_customCert(self):
            result = self.client.algo('util/echo').pipe(bytearray('foo', 'utf-8'))
            self.assertEquals('binary', result.metadata.content_type)
            self.assertEquals(bytearray('foo', 'utf-8'), result.result)

        def test_normal_call(self):
            result = self.client.algo('util/echo').pipe("foo")
            self.assertEquals("text", result.metadata.content_type)
            self.assertEquals("foo", result.result)

        def test_async_call(self):
            result = self.client.algo('util/echo').set_options(output=OutputType.void).pipe("foo")
            self.assertTrue(hasattr(result, "async_protocol"))
            self.assertTrue(hasattr(result, "request_id"))

        def test_raw_call(self):
            result = self.client.algo('util/echo').set_options(output=OutputType.raw).pipe("foo")
            self.assertEquals("foo", result)

        def test_dict_call(self):
            result = self.client.algo('util/echo').pipe({"foo": "bar"})
            self.assertEquals("json", result.metadata.content_type)
            self.assertEquals({"foo": "bar"}, result.result)

        def test_text_unicode(self):
            telephone = u"\u260E"
            # Unicode input to pipe()
            result1 = self.client.algo('util/Echo').pipe(telephone)
            self.assertEquals('text', result1.metadata.content_type)
            self.assertEquals(telephone, result1.result)

            # Unicode return in .result
            result2 = self.client.algo('util/Echo').pipe(result1.result)
            self.assertEquals('text', result2.metadata.content_type)
            self.assertEquals(telephone, result2.result)

        def test_get_build_by_id(self):
            result = self.client.algo("J_bragg/Echo").get_build("1a392e2c-b09f-4bae-a616-56c0830ac8e5")
            print(result)
            self.assertTrue(result.commit_sha is not None)

        def test_get_build_logs(self):
            result = self.client.algo("J_bragg/Echo").get_build_logs("1a392e2c-b09f-4bae-a616-56c0830ac8e5")
            print(result)
            self.assertTrue(result.logs is not None)

        def test_get_scm_status(self):
            result = self.client.algo("J_bragg/Echo").get_scm_status()
            print(result)
            self.assertTrue(result.scm_connection_status is not None)

        def test_exception_ipa_algo(self):
            try:
                result = self.client.algo('zeryx/raise_exception').pipe("")
            except AlgorithmException as e:
                self.assertEqual(e.message, "This is an exception")

if __name__ == '__main__':
    unittest.main()
