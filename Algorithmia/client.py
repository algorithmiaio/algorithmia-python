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
    def postJsonHelper(self, url, inputJson):
        headers = {'Content-Type': 'application/json'}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        data = json.dumps(inputJson)
        response = requests.post(self.apiAddress + url, data=data, headers=headers)
        return response.json()

    # Used internally to http get a file
    def getHelper(self, url):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        return requests.get(self.apiAddress + url, headers=headers)

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
