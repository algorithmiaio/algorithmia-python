'Algorithmia Data API Client (python)'

import re
import json
import tempfile

class datafile:
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

    def put(self, data):
        # Post to data api
        self.client.putHelper(self.url, bytes(data))
        return self

    def putJson(self, data):
        # Post to data api
        json = json.dumps(data)
        self.client.putHelper(self.url, json)
        return self

    def putFile(self, path):
        # Post file to data api
        file = open(path, 'r')
        self.client.putHelper(self.url, file)
        return self

    def delete(self):
        # Delete from data api
        self.client.deleteHelper(self.url)
        return True
