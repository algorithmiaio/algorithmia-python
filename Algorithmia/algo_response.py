import base64
from Algorithmia.errors import AlgorithmException

class AlgoResponse(object):
    def __init__(self, result, metadata):
        self.result = result
        self.metadata = metadata

    def __unicode__(self):
        return 'AlgoResponse(result=%s,metadata=%s)' % (self.result, self.metadata)

    def __repr__(self):
        return self.__unicode__().encode('utf-8')

    @staticmethod
    def create_algo_response(responseJson):
        # Parse response JSON
        if 'error' in responseJson:
            # Failure
            raise parse_exception(responseJson['error'])
        else:
            metadata = Metadata(responseJson['metadata'])
            # Success, check content_type
            if responseJson['metadata']['content_type'] == 'binary':
                # Decode Base64 encoded binary file
                return AlgoResponse(base64.b64decode(responseJson['result']), metadata)
            elif responseJson['metadata']['content_type'] == 'void':
                return AlgoResponse(None, metadata)
            else:
                return AlgoResponse(responseJson['result'], metadata)


def parse_exception(error):
    message = error['message']
    if 'stacktrace' in error:
        stacktrace = error['stacktrace']
    else:
        stacktrace = None
    if 'error_type' in error:
        error_type = error['error_type']
    else:
        error_type = None
    e = AlgorithmException(message=message, error_type=error_type)
    e.stacktrace = stacktrace
    return e

class Metadata(object):
    def __init__(self, metadata):
        self.content_type = metadata['content_type']
        self.duration = metadata['duration']
        self.stdout = None
        if 'stdout' in metadata:
            self.stdout = metadata['stdout']
        self.full_metadata = metadata

    def __repr__(self):
        return "Metadata(content_type='%s',duration=%s,stdout=%s)" % (self.content_type, self.duration, self.stdout)
