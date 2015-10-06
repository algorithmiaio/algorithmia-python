'Algorithmia Data API Client (python)'

import re
import json
import tempfile

class datafile(object):
    def __init__(self, client, dataUrl):
        self.client = client
        # Parse dataUrl
        self.path = re.sub(r'^data://|^/', '', dataUrl)
        self.url = '/v1/data/' + self.path

    # Deprecated:
    def get(self):
        return self.client.getHelper(self.url)

    # Get file from the data api
    def getFile(self):
        # Make HTTP get request
        response = self.client.getHelper(self.url)
        with tempfile.NamedTemporaryFile(delete = False) as f:
            for block in response.iter_content(1024):
                if not block:
                    break;
                f.write(block)
            f.flush()
            return open(f.name)

    def getBytes(self):
        # Make HTTP get request
        return self.client.getHelper(self.url).content

    def getString(self):
        # Make HTTP get request
        return self.client.getHelper(self.url).text

    def getJson(self):
        # Make HTTP get request
        return self.client.getHelper(self.url).json()

    def exists(self):
        response = self.client.headHelper(self.url)
        return (response.status_code == 200)

    def put(self, data):
        # Post to data api
        result = self.client.putHelper(self.url, bytes(data))
        if 'error' in result:
            raise Exception(result['error']['message'])
        else:
            return self

    def putJson(self, data):
        # Post to data api
        jsonElement = json.dumps(data)
        result = self.client.putHelper(self.url, jsonElement)
        if 'error' in result:
            raise Exception(result['error']['message'])
        else:
            return self

    def putFile(self, path):
        # Post file to data api
        with open(path, 'r') as f:
            result = self.client.putHelper(self.url, f)
            if 'error' in result:
                raise Exception(result['error']['message'])
            else:
                return self

    def delete(self):
        # Delete from data api
        result = self.client.deleteHelper(self.url)
        if 'error' in result:
            raise Exception(result['error']['message'])
        else:
            return True
