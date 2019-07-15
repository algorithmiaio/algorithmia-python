import sys
sys.path.append("../")
from unittest.mock import patch
import json
import unittest
import os
from subprocess import Popen, PIPE
import Algorithmia
from Test.handler_algorithms import basic

class HandlerTest(unittest.TestCase):
    fifo_pipe = "/tmp/algoout"

    def setUp(self):
        try:
            os.mkfifo(self.fifo_pipe, mode=0o644)
        except:
            pass

    def tearDown(self):
        os.remove(self.fifo_pipe)

    def test_basic(self):
        input = {'content_type': 'json', 'data': 'Algorithmia'}
        expected_output = "hello Algorithmia"
        apply = basic.apply
        load = basic.load
        pipe = os.open(self.fifo_pipe, os.O_RDONLY | os.O_NONBLOCK)
        algo = Algorithmia.handler(apply, load)
        sys.stdin = [str(json.dumps(input))]
        algo.serve()
        actual_output = json.loads(os.read(pipe, 100))
        os.close(pipe)
        self.assertEqual(expected_output, actual_output['result'])
    