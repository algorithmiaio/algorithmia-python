'Algorithmia API Client (python)'

import Algorithmia
from Algorithmia.insights import Insights
from Algorithmia.algorithm import Algorithm
from Algorithmia.datafile import DataFile, LocalDataFile
from Algorithmia.datadirectory import DataDirectory, LocalDataDirectory
from algorithmia_api_client import Configuration, DefaultApi, ApiClient

from tempfile import mkstemp
import atexit
import json, re, requests, six, certifi
import os


class Client(object):
    'Algorithmia Common Library'
   

    handle, ca_cert = None,None
    apiKey = None
    apiAddress = None
    requestSession = None


    def __init__(self, apiKey = None, apiAddress = None, caCert = None):
        # Override apiKey with environment variable
        self.requestSession = requests.Session()
        if apiKey is None and 'ALGORITHMIA_API_KEY' in os.environ:
            apiKey = os.environ['ALGORITHMIA_API_KEY']
        self.apiKey = apiKey
        if apiAddress is not None:
            self.apiAddress = apiAddress
        else:
            self.apiAddress = Algorithmia.getApiAddress()
        if caCert is None and 'REQUESTS_CA_BUNDLE' in os.environ:
            caCert = os.environ.get('REQUESTS_CA_BUNDLE')
            self.catCerts(caCert)
            self.requestSession.verify = self.ca_cert
        elif caCert is not None and 'REQUESTS_CA_BUNDLE' not in os.environ:
            self.catCerts(caCert)
            self.requestSession.verify = self.ca_cert
        elif caCert is not None and 'REQUESTS_CA_BUNDLE' in os.environ:
            #if both are available, use the one supplied in the constructor. I assume that a user supplying a cert in initialization wants to use that one. 
            self.catCerts(caCert)
            self.requestSession.verify = self.ca_cert


        config = Configuration()
        config.api_key['Authorization'] = self.apiKey
        config.host = "{}/v1".format(self.apiAddress)
        self.manageApi = DefaultApi(ApiClient(config))
        
    def algo(self, algoRef):
        return Algorithm(self, algoRef)

    def username(self):
        username = next(self.dir("").list()).path
        return username

    def file(self, dataUrl):
        if dataUrl.startswith('file://'): return LocalDataFile(self, dataUrl)
        else: return DataFile(self, dataUrl)

    def dir(self, dataUrl):
        if dataUrl.startswith('file://'): return LocalDataDirectory(self, dataUrl)
        else: return DataDirectory(self, dataUrl)

    def create_user(self, requestString):
        url = "/v1/users" 
        response = self.postJsonHelper(url,input_object=requestString)
        return response

    def get_org_types(self):
        url = "/v1/organization/types"
        response = self.getHelper(url)
        return json.loads(response.content.decode("utf-8"))

    def create_org(self,requestString):
        url = "/v1/organizations"
        type = requestString["type_id"]

        id,error = self.convert_type_id(type)
        requestString["type_id"] = id
        
        response = self.postJsonHelper(url=url,input_object=requestString)
        if (error != "") and (response["error"] is not None):
            response["error"]["message"] = error

        return response
    
    def get_org(self,org_name):
        url = "/v1/organizations/"+org_name
        response = self.getHelper(url)
        return json.loads(response.content.decode("utf-8"))

    def edit_org(self,org_name,requestString):
        url = "/v1/organizations/"+org_name
        type = requestString["type_id"]

        id,error = self.convert_type_id(type)
        requestString["type_id"] = id

        data = json.dumps(requestString).encode('utf-8')
        response = self.putHelper(url,data)

        if (error != "") and (response["error"] is not None):
            response["error"]["message"] = error

        return response

    def invite_to_org(self,orgname,username):
        url = "/v1/organizations/"+orgname+"/members/"+username
        response = self.putHelper(url,data={})
        return response

    # Used to send insight data to Algorithm Queue Reader in cluster
    def report_insights(self, insights):
        return Insights(insights)


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

        response = self.requestSession.post(self.apiAddress + url, data=input_json, headers=headers, params=query_parameters)

        if parse_response_as_json:
            return response.json()
        return response

    # Used internally to http get a file
    def getHelper(self, url, **query_parameters):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        return self.requestSession.get(self.apiAddress + url, headers=headers, params=query_parameters)

    def patchHelper(self, url, params):
        headers = {'content-type': 'application/json'}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        return self.requestSession.patch(self.apiAddress + url, headers=headers, data=json.dumps(params))

    # Used internally to get http head result
    def headHelper(self, url):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        return self.requestSession.head(self.apiAddress + url, headers=headers)


    # Used internally to http put a file
    def putHelper(self, url, data):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        if isJson(data):
            headers['Content-Type'] = 'application/json'

        response = self.requestSession.put(self.apiAddress + url, data=data, headers=headers)
        if response._content == b'':
            return response
        return response.json()

    # Used internally to http delete a file
    def deleteHelper(self, url):
        headers = {}
        if self.apiKey is not None:
            headers['Authorization'] = self.apiKey
        response = self.requestSession.delete(self.apiAddress + url, headers=headers)
        if response.reason == "No Content":
            return response
        return response.json()

    # Used internally to concatonate given custom cert with built in certificate store. 
    def catCerts(self,customCert):
        self.handle, self.ca_cert = mkstemp(suffix = ".pem")
        #wrapped all in the with context handler to prevent unclosed files
        with open(customCert,'r') as custom_cert, \
            open(self.ca_cert,'w') as ca,\
            open(certifi.where(),'r') as cert:
                new_cert = custom_cert.read() + cert.read()
                ca.write(new_cert)
        atexit.register(self.exit_handler)
    
    #User internally to convert type id name to uuid
    def convert_type_id(self,type):
        id=""
        error=""
        types = self.get_org_types()
        for enumtype in types:
            if type == enumtype["name"]:
                id = enumtype["id"]
                error=""
                break
            else:
                error = "invalid type_id"
                
        return(id,error)


    # Used internally to clean up temporary files
    def exit_handler(self):
        try:
            os.close(self.handle)
            os.unlink(self.ca_cert)
        except OSError as e:
            print(e)   

def isJson(myjson):
    try:
        json_object = json.loads(myjson)
    except (ValueError,TypeError) as e:
        return False

    return True