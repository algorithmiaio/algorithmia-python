'Algorithmia API Client (python)'

import Algorithmia
from Algorithmia.algorithm import algorithm
from Algorithmia.data import datafile

import json, re, requests

class client(object):
    'Algorithmia Common Library'

    apiKey = None
    apiAddress = None

    def __init__(self, apiKey = None, apiAddress = None):
        self.apiKey = apiKey
        if apiAddress is not None:
            self.apiAddress = apiAddress
        else:
            self.apiAddress = Algorithmia.getApiAddress()

    def algo(self, algoRef):
        return algorithm(self, algoRef)

    def file(self, dataUrl):
        return datafile(self, dataUrl)

    # Used internally to post json to the api and parse json response
    def postJsonHelper(self, url, input_object):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey

        input_json = None
        content_type = "void"
        if input_object is None:
            input_json = json.dumps(None)
            headers['Content-Type'] = 'application/json'
        elif isinstance(input_object, basestring):
            input_json = input_object
            headers['Content-Type'] = 'text/plain'
        elif isinstance(input_object, bytearray):
            input_json = input_object
            headers['Content-Type'] = 'application/octet-stream'
        else:
            input_json = json.dumps(input_object)
            headers['Content-Type'] = 'application/json'

        response = requests.post(self.apiAddress + url, data=input_json, headers=headers)
        return response.json()

    # Used internally to http get a file
    def getHelper(self, url):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        return requests.get(self.apiAddress + url, headers=headers)

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
