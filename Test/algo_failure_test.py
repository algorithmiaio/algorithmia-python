
from multiprocessing import Process

import unittest
import Algorithmia
import uvicorn
import time
from requests import Response
from api import app

def start_webserver():
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="debug")

class AlgoTest(unittest.TestCase):
    error_500 = Response()
    error_500.status_code = 500

    def setUp(self):
        self.client = Algorithmia.client(api_address="http://localhost:8080", api_key="")
        self.uvi_p = Process(target=start_webserver)
        self.uvi_p.start()
        time.sleep(1)
    def tearDown(self):
        self.uvi_p.terminate()
    def test_throw_500_error_HTTP_response_on_algo_request(self):
        try:
            result = self.client.algo('util/Echo').pipe(bytearray('foo','utf-8'))
        except Exception as e:
            result = e
            pass
        self.assertEqual(str(self.error_500), str(result))
