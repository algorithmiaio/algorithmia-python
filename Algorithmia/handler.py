import sys
import json
import base64
import traceback
import six

class Handler(object):

    def __init__(self, apply, load=None):
        self.apply = apply
        self.FIFO_PATH = "/tmp/algoout"
        if load:
            self.load = load
        else:
            self.load = lambda: None

    def load(self):
        load_result = self.load()
        sys.stdout.flush("PIPE_INIT_COMPLETE")
        return load_result

    def format_data(self, request):
        if request['content_type'] in ['text', 'json']:
            data = request['data']
        elif request['content_type'] == 'binary':
            data = self.wrap_binary_data(request['data'])
        else:
            raise Exception("Invalid content_type: {}".format(request['content_type']))
        return data

    def is_binary(self, arg):
        if six.PY3:
            return isinstance(arg, base64.bytes_types)

        return isinstance(arg, bytearray)

    def wrap_binary_data(self, data):
        if six.PY3:
            return bytes(data)
        else:
            return bytearray(data)

    def format_response(self, response):
        if self.is_binary(response):
            content_type = 'binary'
            response = base64.b64encode(response)
            if not isinstance(response, six.string_types):
                response = str(response, 'utf-8')
        elif isinstance(response, six.string_types) or isinstance(response, six.text_type):
            content_type = 'text'
        else:
            content_type = 'json'
        response_string = json.dumps({
            'result': response,
            'metadata': {
                'content_type': content_type
            }
        })
        return response_string

    def write_to_pipe(self, data_string):
        sys.stdout.flush()

        with open(self.FIFO_PATH, 'w') as f:
            f.write(data_string)
            f.write('\n')

    def serve(self):
        try:
            load_result = self.load()
            for line in sys.stdin:
                request = json.loads(line)
                formatted_input = self.format_data(request)
                if load_result:
                    apply_result = self.apply(formatted_input, load_result)
                else:
                    apply_result = self.apply(formatted_input)
                formatted_response = self.format_response(apply_result)
                self.write_to_pipe(formatted_response)
        except Exception as e:
            if hasattr(e, 'error_type'):
                error_type = e.error_type
            else:
                error_type = 'AlgorithmError'
            response_string = json.dumps({
                'error': {
                    'message': str(e),
                    'stacktrace': traceback.format_exc(),
                    'error_type': error_type
                }
            })
            self.write_to_pipe(response_string)