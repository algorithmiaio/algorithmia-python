'Algorithmia Data API Client (python)'

import re
import json
import six
import tempfile
from datetime import datetime
import os.path

from Algorithmia.util import getParentAndBase
from Algorithmia.data import DataObject, DataObjectType
from Algorithmia.errors import DataApiError

class DataFile(DataObject):
    def __init__(self, client, dataUrl):
        super(DataFile, self).__init__(DataObjectType.file)
        self.client = client
        # determine whether file is local or in Algorithmia data://
        self.is_local = not dataUrl.startswith('data://')
        # Parse dataUrl
        self.path = re.sub(r'^data://|^/', '', dataUrl)
        self.url = '/v1/data/' + self.path
        self.last_modified = None
        self.size = None

    def set_attributes(self, attributes):
        self.last_modified = datetime.strptime(attributes['last_modified'],'%Y-%m-%dT%H:%M:%S.%fZ')
        self.size = attributes['size']

    # Deprecated:
    def get(self):
        return self.client.getHelper(self.url)

    # Get file from the data api
    def getFile(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        if self.is_local:
            return open(self.path)
        # Make HTTP get request
        response = self.client.getHelper(self.url)
        with tempfile.NamedTemporaryFile(delete = False) as f:
            for block in response.iter_content(1024):
                if not block:
                    break;
                f.write(block)
            f.flush()
            return open(f.name)

    def getName(self):
        _, name = getParentAndBase(self.path)
        return name

    def getBytes(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        if self.is_local:
            f = open(self.path, 'rb')
            bts = f.read()
            f.close()
            return bts
        # Make HTTP get request
        return self.client.getHelper(self.url).content

    def getString(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        if self.is_local:
            with open(self.path, 'r') as f: return f.read()
        # Make HTTP get request
        return self.client.getHelper(self.url).text

    def getJson(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        if self.is_local:
            return json.loads(open(self.path, 'r').read())
        # Make HTTP get request
        return self.client.getHelper(self.url).json()

    def exists(self):
        # In order to not break backward compatability keeping this method to only return
        # a boolean
        exists, error = self.existsWithError()
        return exists

    def existsWithError(self):
        if self.is_local:
            return os.path.isfile(self.path), ''
        response = self.client.headHelper(self.url)
        error = None
        if 'X-Error-Message' in response.headers:
            error = response.headers['X-Error-Message']
        return (response.status_code == 200, error)

    def put(self, data):
        # First turn the data to bytes if we can
        if isinstance(data, six.string_types) and not isinstance(data, six.binary_type):
            data = bytes(data.encode())
        if self.is_local:
            with open(self.path, 'wb') as f: f.write(data)
            return self
        # Post to data api
        if isinstance(data, six.binary_type):
            result = self.client.putHelper(self.url, data)
            if 'error' in result:
                raise DataApiError(result['error']['message'])
            else:
                return self
        else:
            raise TypeError("Must put strings or binary data. Use putJson instead")

    def putJson(self, data):
        # Post to data api
        jsonElement = json.dumps(data)
        if self.is_local:
            result = localPutHelper(self.path, jsonElement)
            if 'error' in result: raise DataApiError(result['error']['message'])
            else: return self
        result = self.client.putHelper(self.url, jsonElement)
        if 'error' in result:
            raise DataApiError(result['error']['message'])
        else:
            return self

    def putFile(self, path):
        if self.is_local:
            result = localPutHelper(path, self.path)
            if 'error' in result: raise DataApiError(result['error']['message'])
            else: return self
        # Post file to data api
        with open(path, 'rb') as f:
            result = self.client.putHelper(self.url, f)
            if 'error' in result:
                raise DataApiError(result['error']['message'])
            else:
                return self

    def delete(self):
        if self.is_local:
            try:
                os.remove(self.path)
                return True
            except: raise DataApiError('Failed to delete local file ' + self.path)
        # Delete from data api
        result = self.client.deleteHelper(self.url)
        if 'error' in result:
            raise DataApiError(result['error']['message'])
        else:
            return True

def localPutHelper(path, contents):
    try:
        with open(path, 'wb') as f:
            f.write(contents)
            return dict(status='success')
    except Exception as e: return dict(error=str(e))
