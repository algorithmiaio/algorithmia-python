'Algorithmia Data API Client (python)'

import json
import re
import os
import six
import tempfile

import Algorithmia
from Algorithmia.datafile import DataFile
from Algorithmia.data import DataObject, DataObjectType
from Algorithmia.errors import DataApiError
from Algorithmia.util import getParentAndBase, pathJoin
from Algorithmia.acl import Acl

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

    def set_attributes(self, response_json):
        # Nothing to set for now
        pass

    def getName(self):
        _, name = getParentAndBase(self.path)
        return name

    def exists(self):
        # Heading a directory apparently isn't a valid operation
        response = self.client.getHelper(self.url)
        return (response.status_code == 200)

    def create(self, acl=None):
        '''Creates a directory, optionally include Acl argument to set permissions'''
        parent, name = getParentAndBase(self.path)
        json = { 'name': name }
        if acl is not None:
            json['acl'] = acl.to_api_param()
        response = self.client.postJsonHelper(DataDirectory._getUrl(parent), json, False)
        if (response.status_code != 200):
            raise DataApiError("Directory creation failed: " + str(response.content))

    def delete(self, force=False):
        # Delete from data api
        url = self.url
        if force:
            url += '?force=true'

        result = self.client.deleteHelper(url)
        if 'error' in result:
            raise DataApiError(result['error']['message'])
        else:
            return True

    def file(self, name):
        return DataFile(self.client, pathJoin(self.path, name))

    def files(self):
        return self._get_directory_iterator(DataObjectType.file)

    def dir(self, name):
        return DataDirectory(self.client, pathJoin(self.path, name))

    def dirs(self):
        return self._get_directory_iterator(DataObjectType.directory)

    def list(self):
        return self._get_directory_iterator()

    def get_permissions(self):
        '''
        Returns permissions for this directory or None if it's a special collection such as
        .session or .algo
        '''
        response = self.client.getHelper(self.url, acl='true')
        if response.status_code != 200:
            raise DataApiError('Unable to get permissions:' + str(response.content))
        content = response.json()
        if 'acl' in content:
            return Acl.from_acl_response(content['acl'])
        else:
            return None

    def update_permissions(self, acl):
        params = {'acl':acl.to_api_param()}
        response = self.client.patchHelper(self.url, params)
        if response.status_code != 200:
            raise DataApiError('Unable to update permissions: ' + response.json()['error']['message'])
        return True

    def _get_directory_iterator(self, type_filter=None):
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
                raise DataApiError("Directory iteration failed: " + str(response.content))

            responseContent = response.content
            if isinstance(responseContent, six.binary_type):
                responseContent = responseContent.decode()

            content = json.loads(responseContent)
            if 'marker' in content:
                marker = content['marker']
            else:
                marker = None

            if type_filter is DataObjectType.directory or type_filter is None:
                for d in self._iterate_directories(content):
                    yield d
            if type_filter is DataObjectType.file or type_filter is None:
                for f in self._iterate_files(content):
                    yield f

    def _iterate_directories(self, content):
        directories = []
        if 'folders' in content:
            for dir_info in content['folders']:
                d = DataDirectory(self.client, pathJoin(self.path, dir_info['name']))
                d.set_attributes(dir_info)
                directories.append(d)
        return directories

    def _iterate_files(self, content):
        files = []
        if 'files' in content:
            for file_info in content['files']:
                f = DataFile(self.client, pathJoin(self.path, file_info['filename']))
                f.set_attributes(file_info)
                files.append(f)
        return files


class LocalDataDirectory():
    def __init__(self, client, dataUrl):
        self.client = client
        # Parse dataUrl
        self.path = dataUrl.replace('file://', '')

    def set_attributes(self, response_json):
        raise NotImplementedError

    def getName(self):
        raise NotImplementedError

    def exists(self):
        return os.path.isdir(self.path)

    def create(self):
        os.mkdir(self.path)

    def delete(self, force=False):
        os.rmdir(self.path)

    def file(self, name):
        return LocalDataFile(self.client, 'file://' + pathJoin(self.path, name))

    def dir(self, name):
        raise NotImplementedError

    def list(self):
        for x in os.listdir(self.path): yield x

    def dirs(self, content):
        for x in os.listdir(self.path):
            if os.path.isdir(self.path+'/'+x): yield x

    def files(self, content):
        for x in os.listdir(self.path):
            if os.path.isfile(self.path+'/'+x): yield x
