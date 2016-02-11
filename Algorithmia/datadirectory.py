'Algorithmia Data API Client (python)'

import json
import re
import tempfile
import urllib

import Algorithmia
from Algorithmia.data import datafile
from Algorithmia.util import getParentAndBase, pathJoin

def getUrl(path):
    return '/v1/data/' + path

class DataDirectory(object):
    def __init__(self, client, dataUrl):
        self.client = client
        # Parse dataUrl
        self.path = re.sub(r'^data://|^/', '', dataUrl)
        self.url = getUrl(self.path)

    def getName(self):
        _, name = getParentAndBase(self.path)
        return name

    def exists(self):
        # Heading a directory apparently isn't a valid operation
        response = self.client.getHelper(self.url)
        return (response.status_code == 200)

    def create(self):
        parent, name = getParentAndBase(self.path)
        json = { 'name': name }

        response = self.client.postJsonHelper(getUrl(parent), json, False)
        if (response.status_code != 200):
            raise Exception("Directory creation failed: " + str(response.content))

    def delete(self, force):
        # Delete from data api
        url = self.url
        if force:
            url += '?force=true'

        result = self.client.deleteHelper(url)
        if 'error' in result:
            raise Exception(result['error']['message'])
        else:
            return True

    def file(self, name):
        return datafile(self.client, pathJoin(self.path, name))

    def files(self):
        return self._getDirectoryIterator('files', 'filename')

    def dirs(self):
        return self._getDirectoryIterator('folders', 'name')

    def _getDirectoryIterator(self, contentKey, elementKey):
        marker = None
        first = True
        while first or (marker is not None and len(marker) > 0):
            first = False
            url = self.url
            if marker:
                queryParams = { 'marker': marker }
                url += '?' + urllib.urlencode(queryParams)
            response = self.client.getHelper(url)
            if response.status_code != 200:
                raise Exception("Directory iteration failed: " + str(response.content))

            content = json.loads(response.content)

            if 'marker' in content:
                marker = content['marker']
            else:
                marker = None

            if contentKey in content:
                for f in content[contentKey]:
                    yield datafile(self.client, pathJoin(self.path, f[elementKey]))
