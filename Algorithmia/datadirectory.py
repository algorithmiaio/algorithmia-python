'Algorithmia Data API Client (python)'

import re
import json
import tempfile

class DataDirectory(object):
    def __init__(self, client, dataUrl):
        self.client = client
        # Parse dataUrl
        self.path = re.sub(r'^data://|^/', '', dataUrl)
        self.url = '/v1/data/' + self.path

    def exists(self):
        response = self.client.headHelper(self.url)
        return (response.status_code == 200)