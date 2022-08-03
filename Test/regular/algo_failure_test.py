import sys

if sys.version_info[0] >= 3:
    import unittest
    import Algorithmia
    import uvicorn
    import time
    from multiprocessing import Process

    # look in ../ BEFORE trying to import Algorithmia.  If you append to the
    # you will load the version installed on the computer.
    sys.path = ['../'] + sys.path
    from requests import Response

    class AlgoTest(unittest.TestCase):
        error_500 = Response()
        error_500.status_code = 500
        error_message = "Non-Algorithm related Failure: " + str(error_500)

        @classmethod
        def setUpClass(cls):
            cls.client = Algorithmia.client(api_address="http://localhost:8080", api_key="simabcd123")

        def test_throw_500_error_HTTP_response_on_algo_request(self):
            try:
                result = self.client.algo('util/500').pipe(bytearray('foo', 'utf-8'))
            except Exception as e:
                result = e
                pass
            self.assertEqual(str(self.error_message), str(result))

        def test_retry_on_400_error_publish(self):
            result = self.client.algo("util/failonce").publish()
            self.assertEqual(result['version_info']['semantic_version'], "0.1.0")

        def test_throw_on_always_500_publish(self):
            try:
                result = self.client.algo("util/failalways").publish()
            except Exception as e:
                result = e
                pass
            self.assertEqual(str(self.error_message), str(result))
