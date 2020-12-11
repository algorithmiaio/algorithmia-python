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
    def __init__(self, message, error_type=None):
        self.message = message
        self.error_type = error_type
    def __str__(self):
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
            raise AlgorithmException(result['error']['message'])
        else:
            raise AlgorithmException(result['error'])