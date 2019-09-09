'Algorithmia API Client (python)'

import Algorithmia
from Algorithmia.algorithm import Algorithm
from Algorithmia.datafile import DataFile, LocalDataFile
from Algorithmia.datadirectory import DataDirectory, LocalDataDirectory
from algorithmia_api_client import Configuration, DefaultApi, ApiClient

import json, re, requests, six
import os

class Client(object):
    'Algorithmia Common Library'

    apiKey = None
    apiAddress = None

    def __init__(self, apiKey = None, apiAddress = None):
        # Override apiKey with environment variable
        if apiKey is None and 'ALGORITHMIA_API_KEY' in os.environ:
            apiKey = os.environ['ALGORITHMIA_API_KEY']
        self.apiKey = apiKey
        if apiAddress is not None:
            self.apiAddress = apiAddress
        else:
            self.apiAddress = Algorithmia.getApiAddress()
        config = Configuration()
        config.api_key['Authorization'] = self.apiKey
        config.host = "{}/v1".format(self.apiAddress)
        self.manageApi = DefaultApi(ApiClient(config))

    def algo(self, algoRef):
        return Algorithm(self, algoRef)

    def file(self, dataUrl):
        if dataUrl.startswith('file://'): return LocalDataFile(self, dataUrl)
        else: return DataFile(self, dataUrl)

    def dir(self, dataUrl):
        if dataUrl.startswith('file://'): return LocalDataDirectory(self, dataUrl)
        else: return DataDirectory(self, dataUrl)

    # Used internally to post json to the api and parse json response
    def postJsonHelper(self, url, input_object, parse_response_as_json=True, **query_parameters):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey

        input_json = None
        if input_object is None:
            input_json = json.dumps(None).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif isinstance(input_object, six.string_types):
            input_json = input_object.encode('utf-8')
            headers['Content-Type'] = 'text/plain'
        elif isinstance(input_object, bytearray) or isinstance(input_object, bytes):
            input_json = bytes(input_object)
            headers['Content-Type'] = 'application/octet-stream'
        else:
            input_json = json.dumps(input_object).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        response = requests.post(self.apiAddress + url, data=input_json, headers=headers, params=query_parameters)

        if parse_response_as_json:
            return response.json()
        return response

    # Used internally to http get a file
    def getHelper(self, url, **query_parameters):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        return requests.get(self.apiAddress + url, headers=headers, params=query_parameters)

    def patchHelper(self, url, params):
        headers = {'content-type': 'application/json'}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        return requests.patch(self.apiAddress + url, headers=headers, data=json.dumps(params))

    # Used internally to get http head result
    def headHelper(self, url):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        return requests.head(self.apiAddress + url, headers=headers)

    # Used internally to http put a file
    def putHelper(self, url, data):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        response = requests.put(self.apiAddress + url, data=data, headers=headers)
        return response.json()

    # Used internally to http delete a file
    def deleteHelper(self, url):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        response = requests.delete(self.apiAddress + url, headers=headers)
        return response.json()
