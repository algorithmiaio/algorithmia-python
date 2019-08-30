import sys
import json
import base64
import traceback
import inspect
import six


class Handler(object):

    def __init__(self, apply_func, load_func):
        """
        Creates the handler object
        :param apply_func: A required function that can have an arity of 1-2, depending on if loading occurs
        :param load_func: An optional supplier function used if load time events are required, has an arity of 0.
        """
        self.FIFO_PATH = "/tmp/algoout"
        apply_args, _, _, apply_defaults = inspect.getargspec(apply_func)
        load_args, _, _, _ = inspect.getargspec(load_func)
        if len(load_args) > 0:
            raise Exception("load function must not have parameters")
        if len(apply_args) > 2 or len(apply_args) == 0:
            raise Exception("apply function may have between 1 and 2 parameters, not {}".format(len(apply_args)))
        self.apply_func = apply_func
        self.load_func = load_func
        self.load_result = None

    def load(self):
        self.load_result = self.load_func()
        print('PIPE_INIT_COMPLETE')
        sys.stdout.flush()

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
        with open(self.FIFO_PATH, 'w') as f:
            f.write(data_string)
            f.write('\n')
        sys.stdout.flush()

    def serve(self):
        try:
            self.load()
        except Exception as e:
            if hasattr(e, 'error_type'):
                error_type = e.error_type
            else:
                error_type = 'AlgorithmError'
            load_error_string = json.dumps({
                'error': {
                    'message': str(e),
                    'stacktrace': traceback.format_exc(),
                    'error_type': error_type
                }
            })
            return self.write_to_pipe(load_error_string)
        for line in sys.stdin:
            try:
                request = json.loads(line)
                formatted_input = self.format_data(request)
                if self.load_result:
                    apply_result = self.apply_func(formatted_input, self.load_result)
                else:
                    apply_result = self.apply_func(formatted_input)
                response_string = self.format_response(apply_result)
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
            finally:
                self.write_to_pipe(response_string)