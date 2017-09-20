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
