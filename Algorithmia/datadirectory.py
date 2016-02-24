'Algorithmia Data API Client (python)'

import json
import re
import six
import tempfile

import Algorithmia
from Algorithmia.datafile import DataFile
from Algorithmia.data import DataObject, DataObjectType
from Algorithmia.util import getParentAndBase, pathJoin

class DataDirectory(DataObject):
    def __init__(self, client, dataUrl):
        super(DataDirectory, self).__init__(DataObjectType.directory)
        self.client = client
        # Parse dataUrl
        self.path = re.sub(r'^data://|^/', '', dataUrl)
        self.url = DataDirectory._getUrl(self.path)

    @staticmethod
    def _getUrl(path):
        return '/v1/data/' + path


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

        response = self.client.postJsonHelper(DataDirectory._getUrl(parent), json, False)
        if (response.status_code != 200):
            raise Exception("Directory creation failed: " + str(response.content))

    def delete(self, force=False):
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
        return DataFile(self.client, pathJoin(self.path, name))

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
            query_params= {}
            if marker:
                query_params['marker'] = marker
            response = self.client.getHelper(url, **query_params)
            if response.status_code != 200:
                raise Exception("Directory iteration failed: " + str(response.content))

            responseContent = response.content
            if isinstance(responseContent, six.binary_type):
                responseContent = responseContent.decode()

            content = json.loads(responseContent)
            if 'marker' in content:
                marker = content['marker']
            else:
                marker = None

            if contentKey in content:
                for f in content[contentKey]:
                    yield DataFile(self.client, pathJoin(self.path, f[elementKey]))
