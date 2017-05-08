class ApiError(Exception):
    '''General error from the Algorithmia API'''
    pass

class ApiInternalError(ApiError):
    '''Error representing a server error, typically a 5xx status code'''
    pass

class DataApiError(ApiError):
    '''Error returned from the Algorithmia data API'''
    pass

