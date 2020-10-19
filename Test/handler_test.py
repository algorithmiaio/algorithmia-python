import sys
import json
import unittest
import os
from Test.handler_algorithms import *


class HandlerTest(unittest.TestCase):
    if os.name == "posix":
        fifo_pipe_path = "/tmp/algoout"
    fifo_pipe = None

    def setUp(self):
        try:
            os.mkfifo(self.fifo_pipe_path)
        except Exception:
            pass

    def tearDown(self):
        if os.name == "posix":
            os.remove(self.fifo_pipe_path)

    def read_in(self):
        if os.name == "posix":
            return self.read_from_pipe()
        if os.name == "nt":        
            return self.read_from_stdin()

    def read_from_stdin(self):
        return json.loads(sys.stdin)

    def read_from_pipe(self):
        read_obj = os.read(self.fifo_pipe, 10000)
        if isinstance(read_obj, bytes):
            read_obj = read_obj.decode("utf-8")
        actual_output = json.loads(read_obj)
        os.close(self.fifo_pipe)
        return actual_output

    def open_pipe(self):
        if os.name == "posix":
            self.fifo_pipe = os.open(self.fifo_pipe_path, os.O_RDONLY | os.O_NONBLOCK)

    def execute_example(self, input, apply, load=lambda: None):
        self.open_pipe()
        algo = Algorithmia.handler(apply, load)
        sys.stdin = input
        algo.serve()
        output = self.read_in()
        return output

    def execute_without_load(self, input, apply):
        self.open_pipe()
        algo = Algorithmia.handler(apply)
        sys.stdin = input
        algo.serve()
        output = self.read_in()
        return output



# ----- Tests ----- #

    def test_basic(self):
        input = {'content_type': 'json', 'data': 'Algorithmia'}
        expected_output = {"metadata":
            {
                "content_type": "text"
            },
            "result": "hello Algorithmia"
        }
        input = [str(json.dumps(input))]
        actual_output = self.execute_example(input, apply_input_or_context)
        self.assertEqual(expected_output, actual_output)

    def test_basic_2(self):
        input = {'content_type': 'json', 'data': 'Algorithmia'}
        expected_output = {"metadata":
            {
                "content_type": "text"
            },
            "result": "hello Algorithmia"
        }
        input = [str(json.dumps(input))]
        actual_output = self.execute_without_load(input, apply_basic)
        self.assertEqual(expected_output, actual_output)


    def test_algorithm_loading_basic(self):
        input = {'content_type': 'json', 'data': 'ignore me'}
        expected_output = {'metadata':
            {
                'content_type': 'json'
            },
            'result': {'message': 'This message was loaded prior to runtime'}
        }
        input = [str(json.dumps(input))]
        actual_output = self.execute_example(input, apply_input_or_context, loading_text)
        self.assertEqual(expected_output, actual_output)

    def test_algorithm_loading_algorithmia(self):
        input = {'content_type': 'json', 'data': 'ignore me'}
        expected_output = {'metadata':
            {
                'content_type': 'json'
            },
            'result': {
                'data_url': 'data://demo/collection/somefile.json',
                'data': {'foo': 'bar'}
            }
        }
        input = [str(json.dumps(input))]
        actual_output = self.execute_example(input, apply_input_or_context, loading_file_from_algorithmia)
        self.assertEqual(expected_output, actual_output)

    def test_error_loading(self):
        input = {'content_type': 'json', 'data': 'Algorithmia'}
        expected_output = {'error':
                               {'message': 'This exception was thrown in loading',
                                'error_type': 'AlgorithmError',
                                'stacktrace': ''
                                }
                           }
        input = [str(json.dumps(input))]
        actual_output = self.execute_example(input, apply_input_or_context, loading_exception)
        # beacuse the stacktrace is local path specific,
        # we're going to assume it's setup correctly and remove it from our equality check
        actual_output["error"]["stacktrace"] = ''
        self.assertEqual(expected_output, actual_output)

