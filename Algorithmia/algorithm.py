'Algorithmia Algorithm API Client (python)'

import base64
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
    def pipe(self, input1):
        responseJson = self.client.postJsonHelper(self.url, input1)

        # Parse response JSON
        if 'error' in responseJson:
            # Failure
            raise Exception(responseJson['error']['message'])
        else:
            # Success, check content_type
            if responseJson['metadata']['content_type'] == 'binary':
                # Decode Base64 encoded binary file
                return base64.b64decode(responseJson['result'])
            elif responseJson['metadata']['content_type'] == 'void':
                return None
            else:
                return responseJson['result']
