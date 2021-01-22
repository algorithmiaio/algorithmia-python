class ApiError(Exception):
    '''General error from the Algorithmia API'''
    pass

class ApiInternalError(ApiError):
    '''Error representing a server error, typically a 5xx status code'''
    pass

class DataApiError(ApiError):
    '''Error returned from the Algorithmia data API'''
    pass

class AlgorithmException(ApiError):
    '''Base algorithm error exception'''
    def __init__(self, message, stack_trace=None, error_type=None):
        self.message = message
        self.error_type = error_type
        self.stack_trace = stack_trace
    def __str__(self):
        if self.stack_trace:
            return repr(self.message + "\n" + self.stack_trace)
        else:
            return repr(self.message)


def raiseDataApiError(result):
    if 'error' in result:
        if 'message' in result['error']:
            raise DataApiError(result['error']['message'])
        else:
            raise DataApiError(result['error'])


def raiseAlgoApiError(result):
    if 'error' in result:
        if 'message' in result['error']:
            message = result['error']['message']
        else:
            message = None
        if 'error_type' in result['error']:
            err_type = result['error']['error_type']
        else:
            err_type = None
        if 'stack_trace' in result['error']:
            stacktrace = result['error']['stack_trace']
        else:
            stacktrace = None
        raise AlgorithmException(message=message, stack_trace=stacktrace, error_type=err_type)
