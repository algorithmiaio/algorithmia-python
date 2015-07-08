'Algorithmia Algorithm API Client (python)'
from builtins import object

import re

class algorithm(object):
    def __init__(self, client, algoRef):
        # Parse algoRef
        algoRegex = re.compile(r"(?:algo://|/|)(\w+/.+)")
        m = algoRegex.match(algoRef)
        if m is not None:
            self.client = client
            self.path = m.group(1)
            self.url = '/v1/algo/' + self.path
        else:
            raise Exception('Invalid algorithm URI: ' + algoRef)

    # Pipe an input into this algorithm
    def pipe(self, inputJson):
        responseJson = self.client.postJsonHelper(self.url, inputJson)

        # Parse response JSON
        if 'error' not in responseJson:
            # Success
            return responseJson['result']
        else:
            # Failure
            raise Exception(responseJson['error']['message'])
