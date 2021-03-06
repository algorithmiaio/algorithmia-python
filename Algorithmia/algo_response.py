import base64
from Algorithmia.errors import raiseAlgoApiError
import sys


class AlgoResponse(object):
    def __init__(self, result, metadata):
        self.result = result
        self.metadata = metadata

    def __unicode__(self):
        return 'AlgoResponse(result=%s,metadata=%s)' % (self.result, self.metadata)

    def __repr__(self):
        if sys.version_info[0] >= 3:
            return self.__unicode__()
        else:
            return self.__unicode__().encode('utf-8')

    @staticmethod
    def create_algo_response(responseJson):
        # Parse response JSON
        if 'error' in responseJson:
            # Failure
            raiseAlgoApiError(responseJson)
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

class Metadata(object):
    def __init__(self, metadata):
        self.content_type = metadata['content_type']
        self.duration = metadata['duration']
        self.stdout = None
        if 'stdout' in metadata:
            self.stdout = metadata['stdout']
        self.full_metadata = metadata

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return "Metadata(content_type='%s',duration=%s,stdout=%s)" % (self.content_type, self.duration, self.stdout)
