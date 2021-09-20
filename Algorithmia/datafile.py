'Algorithmia Data API Client (python)'

import re
import json
import six
import tempfile
from datetime import datetime
import os.path
import pkgutil

from Algorithmia.util import getParentAndBase
from Algorithmia.data import DataObject, DataObjectType
from Algorithmia.errors import DataApiError, raiseDataApiError
from io import RawIOBase


class DataFile(DataObject):
    def __init__(self, client, dataUrl):
        super(DataFile, self).__init__(DataObjectType.file)
        self.client = client
        # Parse dataUrl
        self.path = re.sub(r'^data://|^/', '', dataUrl)
        self.url = '/v1/data/' + self.path
        self.last_modified = None
        self.size = None

    def set_attributes(self, attributes):
        self.last_modified = datetime.strptime(attributes['last_modified'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.size = attributes['size']

    # Deprecated:
    def get(self):
        return self.client.getHelper(self.url)

    # Get file from the data api
    def getFile(self, as_path=False):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        # Make HTTP get request
        response = self.client.getHelper(self.url)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            for block in response.iter_content(1024):
                if not block:
                    break
                f.write(block)
            f.flush()
        if as_path:
            return f.name
        else:
            return open(f.name)

    def getName(self):
        _, name = getParentAndBase(self.path)
        return name

    def getBytes(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        # Make HTTP get request
        return self.client.getHelper(self.url).content

    def getString(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        # Make HTTP get request
        return self.client.getHelper(self.url).text

    def getJson(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        # Make HTTP get request
        return self.client.getHelper(self.url).json()

    def getNumpy(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        np_loader = pkgutil.find_loader('numpy')
        if np_loader is not None:
            import numpy as np
            payload = self.client.getHelper(self.url).json()
            return np.array(payload)
        else:
            raise DataApiError("Attempted to .getNumpy() file without numpy available, please install numpy.")

    def exists(self):
        # In order to not break backward compatability keeping this method to only return
        # a boolean
        exists, error = self.existsWithError()
        return exists

    def existsWithError(self):
        response = self.client.headHelper(self.url)
        if 'X-Error-Message' in response.headers:
            error = response.headers['X-Error-Message']
        else:
            error = response.text
        return (response.status_code == 200, error)

    def put(self, data):
        # Post to data api

        # First turn the data to bytes if we can
        if isinstance(data, six.string_types) and not isinstance(data, six.binary_type):
            data = bytes(data.encode())
        if isinstance(data, six.binary_type):
            result = self.client.putHelper(self.url, data)
            if 'error' in result:
                raise raiseDataApiError(result)
            else:
                return self
        else:
            raise TypeError("Must put strings or binary data. Use putJson instead")

    def putJson(self, data):
        # Post to data api
        jsonElement = json.dumps(data)
        result = self.client.putHelper(self.url, jsonElement)
        if 'error' in result:
            raise raiseDataApiError(result)
        else:
            return self

    def putFile(self, path):
        # Post file to data api
        with open(path, 'rb') as f:
            result = self.client.putHelper(self.url, f)
            if 'error' in result:
                raise raiseDataApiError(result)
            else:
                return self

    def putNumpy(self, array):
        # Post numpy array as json payload
        np_loader = pkgutil.find_loader('numpy')
        if np_loader is not None:
            import numpy as np
            encoded_array = array.tolist()
            self.putJson(encoded_array)
            return self
        else:
            raise DataApiError("Attempted to .putNumpy() a file without numpy available, please install numpy.")

    def delete(self):
        # Delete from data api
        result = self.client.deleteHelper(self.url)
        if 'error' in result:
            raise raiseDataApiError(result)
        else:
            return True


class LocalDataFile():
    def __init__(self, client, filePath):
        self.client = client
        # Parse dataUrl
        self.path = filePath.replace('file://', '')
        self.url = '/v1/data/' + self.path
        self.last_modified = None
        self.size = None

    def set_attributes(self, attributes):
        self.last_modified = datetime.strptime(attributes['last_modified'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.size = attributes['size']

    # Get file from the data api
    def getFile(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        return open(self.path)

    def getName(self):
        _, name = getParentAndBase(self.path)
        return name

    def getBytes(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        f = open(self.path, 'rb')
        bts = f.read()
        f.close()
        return bts

    def getString(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        with open(self.path, 'r') as f: return f.read()

    def getJson(self):
        exists, error = self.existsWithError()
        if not exists:
            raise DataApiError('unable to get file {} - {}'.format(self.path, error))
        return json.loads(open(self.path, 'r').read())

    def exists(self):
        return self.existsWithError()[0]

    def existsWithError(self):
        return os.path.isfile(self.path), ''

    def put(self, data):
        # First turn the data to bytes if we can
        if isinstance(data, six.string_types) and not isinstance(data, six.binary_type):
            data = bytes(data.encode())
        with open(self.path, 'wb') as f: f.write(data)
        return self

    def putJson(self, data):
        # Post to data api
        jsonElement = json.dumps(data)
        result = localPutHelper(self.path, jsonElement)
        if 'error' in result:
            raise raiseDataApiError(result)
        else:
            return self

    def putFile(self, path):
        result = localPutHelper(path, self.path)
        if 'error' in result:
            raise raiseDataApiError(result)
        else:
            return self

    def delete(self):
        try:
            os.remove(self.path)
            return True
        except:
            raise DataApiError('Failed to delete local file ' + self.path)


def localPutHelper(path, contents):
    try:
        with open(path, 'wb') as f:
            f.write(contents)
            return dict(status='success')
    except Exception as e:
        return dict(error=str(e))


class AdvancedDataFile(DataFile, RawIOBase):
    def __init__(self, client, dataUrl, cleanup=True):
        super(AdvancedDataFile, self).__init__(client, dataUrl)
        self.cleanup = cleanup
        self.local_file = None

    def __del__(self):
        if self.local_file:
            filepath = self.local_file.name
            self.local_file.close()
            if self.cleanup:
                    os.remove(filepath)

    def readable(self):
        return True

    def seekable(self):
        return True

    def writable(self):
        return False

    def read(self, __size=None):
        if not self.local_file:
            self.local_file = self.getFile()
            output = self.local_file.read()
        elif __size:
            output = self.local_file.read(__size)
        else:
            output = self.local_file.read()
        return output

    def readline(self, __size=None):
        if not self.local_file:
            self.local_file = self.getFile()
        with self.local_file as f:
            if __size:
                output = f.readline(__size)
            else:
                output = f.readline()
        return output

    def readlines(self, __hint=None):
        if not self.local_file:
            self.local_file = self.getFile()
        if __hint:
            output = self.local_file.readlines(__hint)
        else:
            output = self.local_file.readlines()
        return output

    def tell(self):
        if not self.local_file:
            self.local_file = self.getFile()
        output = self.local_file.tell()
        return output

    def seek(self, __offset, __whence=None):
        if not self.local_file:
            self.local_file = self.getFile()
        if __whence:
            output = self.local_file.seek(__offset, __whence)
        else:
            output = self.local_file.seek(__offset)
        return output
