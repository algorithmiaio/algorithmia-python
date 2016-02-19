'Algorithmia Algorithm API Client (python)'

import base64
import re
from async_response import AsyncResponse

class algorithm(object):
    def __init__(self, client, algoRef, **query_parameters):
        # Parse algoRef
        algoRegex = re.compile(r"(?:algo://|/|)(\w+/.+)")
        m = algoRegex.match(algoRef)
        if m is not None:
            self.client = client
            self.path = m.group(1)
            self.url = '/v1/algo/' + self.path
            self.query_parameters = query_parameters
            self.output = None
            if 'output' in query_parameters:
                self.output = query_parameters['output']
        else:
            raise Exception('Invalid algorithm URI: ' + algoRef)

    # Pipe an input into this algorithm
    def pipe(self, input1):
        if self.output == 'raw':
            return self.__postRawOutput(input1)
        elif self.output == 'void':
            return self.__postVoidOutput(input1)
        else:
            responseJson = self.client.postJsonHelper(self.url, input1, **self.query_parameters)

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

    def __postRawOutput(self, input1):
            # Don't parse response as json
            response = self.client.postJsonHelper(self.url, input1, parse_response_as_json=False, **self.query_parameters)
            # Check HTTP code and throw error as needed
            if response.status_code == 400:
                # Bad request
                raise Exception(response.text)
            elif response.status_code == 500:
                raise Exception(response.text)
            else:
                return response.text

    def __postVoidOutput(self, input1):
            responseJson = self.client.postJsonHelper(self.url, input1, **self.query_parameters)
            if 'error' in responseJson:
                raise Exception(responseJson['error']['message'])
            else:
                return AsyncResponse(responseJson)
