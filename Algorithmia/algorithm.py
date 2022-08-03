'Algorithmia Algorithm API Client (python)'

import json
import re
from Algorithmia.async_response import AsyncResponse
from Algorithmia.algo_response import AlgoResponse
from Algorithmia.errors import ApiError, ApiInternalError, raiseAlgoApiError, AlgorithmException
from enum import Enum
from algorithmia_api_client.rest import ApiException
from algorithmia_api_client import CreateRequest, UpdateRequest, VersionRequest, Details, Settings, SettingsMandatory, \
    SettingsPublish, \
    CreateRequestVersionInfo, VersionInfo, VersionInfoPublish

OutputType = Enum('OutputType', 'default raw void')


class Algorithm(object):
    def __init__(self, client, algoRef):
        # Parse algoRef
        algoRegex = re.compile(r"(?:algo://|/|)(\w+/.+)")
        m = algoRegex.match(algoRef)
        if m is not None:
            self.client = client
            self.path = m.group(1)
            self.username = self.path.split("/")[0]
            self.algoname = self.path.split("/")[1]
            if len(self.path.split("/")) > 2:
                self.version = self.path.split("/")[2]
            self.url = '/v1/algo/' + self.path
            self.query_parameters = {}
            self.output_type = OutputType.default
        else:
            raise ValueError('Invalid algorithm URI: ' + algoRef)

    def set_options(self, timeout=300, stdout=False, output=OutputType.default, **query_parameters):
        self.query_parameters = {'timeout': timeout, 'stdout': stdout}
        self.output_type = output
        self.query_parameters.update(query_parameters)
        return self

    def get_algorithm_id(self):
        url = '/v1/algorithms/' + self.username + '/' + self.algoname
        print(url)
        api_response = self.client.getJsonHelper(url)
        if 'id' in api_response:
            return api_response['id']
        else:
            raise Exception("field 'id' not found in response: ", api_response)


    def get_secrets(self):
        algorithm_id = self.get_algorithm_id()
        url = "/v1/algorithms/" + algorithm_id + "/secrets"
        api_response = self.client.getJsonHelper(url)
        return api_response


    def set_secret(self, short_name, secret_key, secret_value, description=None):
        algorithm_id = self.get_algorithm_id()
        url = "/v1/algorithms/" + algorithm_id + "/secrets"
        secret_providers = self.client.get_secret_providers()
        provider_id = secret_providers[0]['id']

        create_parameters = {
            "owner_type": "algorithm",
            "owner_id": algorithm_id,
            "short_name": short_name,
            "provider_id": provider_id,
            "secret_key": secret_key,
            "secret_value": secret_value,
        }
        if description:
            create_parameters['description'] = description
        else:
            create_parameters['description'] = " "

        print(create_parameters)
        api_response = self.client.postJsonHelper(url, create_parameters, parse_response_as_json=True)
        return api_response


    # Create a new algorithm
    def create(self, details, settings, version_info=None, source=None, scmsCredentials=None):
        url = "/v1/algorithms/" + self.username
        create_parameters = {"name": self.algoname, "details": details, "settings": settings}
        if version_info:
            create_parameters['version_info'] = version_info
        if source:
            create_parameters['source'] = source
        if scmsCredentials:
            create_parameters['scmsCredentials'] = scmsCredentials

        api_response = self.client.postJsonHelper(url, create_parameters, parse_response_as_json=True)
        return api_response

    # Update the settings in an algorithm
    def update(self, details={}, settings={}, version_info={}, source={}, scmsCredentials={}):
        url = "/v1/algorithms/" + self.username + "/" + self.algoname
        update_parameters = {"details": details, "settings": settings,
                         "version_info": version_info, "source": source, "scmsCredentials": scmsCredentials}
        api_response = self.client.putHelper(url, update_parameters)
        return api_response

    # Publish an algorithm
    def publish(self, details={}, settings={}, version_info={}, source={}, scmsCredentials={}):
        url = "/v1/algorithms/" + self.username + "/" + self.algoname + "/versions"
        publish_parameters = {"details": details, "settings": settings,
                              "version_info": version_info, "source": source, "scmsCredentials": scmsCredentials}
        api_response = self.client.postJsonHelper(url, publish_parameters, parse_response_as_json=True, retry=True)
        return api_response

    def get_builds(self, limit=56, marker=None):
        kwargs = {"limit": limit, "marker": marker}
        url = "/v1/algorithms/" + self.username + "/" + self.algoname + '/builds'
        response = self.client.getJsonHelper(url, **kwargs)
        return response

    def get_build(self, build_id):
        # Get the build object for a given build_id
        # The build status can have one of the following value: succeeded, failed, in-progress
        url = '/v1/algorithms/' + self.username + '/' + self.algoname + '/builds/' + build_id
        response = self.client.getJsonHelper(url)
        return response

    def get_build_logs(self, build_id):
        # Get the algorithm build logs for a given build_id
        url = '/v1/algorithms/' + self.username + '/' + self.algoname + '/builds/' + build_id + '/logs'
        response = self.client.getJsonHelper(url)
        return response

    def get_scm_status(self):
        url = '/v1/algorithms/' + self.username + '/' + self.algoname + '/scm/status'
        response = self.client.getJsonHelper(url)
        return response

    # Get info on an algorithm
    def info(self, algo_hash=None):
        # Get Algorithm
        if algo_hash:
            url = '/v1/algorithms/' + self.username + '/' + self.algoname + '/versions/' + algo_hash
        else:
            url = '/v1/algorithms/' + self.username + '/' + self.algoname + '/versions'
        response = self.client.getJsonHelper(url)
        return response

    # Check if an Algorithm exists
    def exists(self):
        try:
            url = '/v1/algorithms/' + self.username + '/' + self.algoname
            _ = self.client.getJsonHelper(url)
            return True
        except AlgorithmException as e:
            if "404" in str(e) or "No such algorithm" in str(e):
                return False
            elif "403" in str(e):
                raise Exception("unable to check exists on algorithms you don't own.")
            else:
                raise e

    # Get all versions of the algorithm, with the given filters
    def versions(self, limit=None, marker=None, published=None, callable=None):
        kwargs = {}
        bools = ["True", "False"]
        if limit:
            kwargs["limit"] = limit
        if marker:
            kwargs["marker"] = marker
        if published:
            p = published
            kwargs["published"] = str(p).lower() if str(p) in bools else p
        if callable:
            c = callable
            kwargs["callable"] = str(c).lower() if str(c) in bools else c
        # Get Algorithm versions
        url = '/v1/algorithms/' + self.username + '/' + self.algoname + '/versions'
        response = self.client.getJsonHelper(url, **kwargs)
        return response

    # Compile an algorithm
    def compile(self):
        # Compile algorithm
        url = '/v1/algorithms/' + self.username + '/' + self.algoname + '/compile'
        response = self.client.postJsonHelper(url, {}, parse_response_as_json=True, retry=True)
        return response

    # Pipe an input into this algorithm
    def pipe(self, input1):

        if self.output_type == OutputType.raw:
            return self._postRawOutput(input1)
        elif self.output_type == OutputType.void:
            return self._postVoidOutput(input1)
        else:
            return AlgoResponse.create_algo_response(
                self.client.postJsonHelper(self.url, input1, **self.query_parameters))

    def _postRawOutput(self, input1):
        # Don't parse response as json
        self.query_parameters['output'] = 'raw'
        response = self.client.postJsonHelper(self.url, input1, parse_response_as_json=False, **self.query_parameters)
        # Check HTTP code and throw error as needed
        if response.status_code == 400:
            # Bad request
            raise ApiError(response.text)
        elif response.status_code == 500:
            raise ApiInternalError(response.text)
        else:
            return response.text

    def _postVoidOutput(self, input1):
        self.query_parameters['output'] = 'void'
        responseJson = self.client.postJsonHelper(self.url, input1, **self.query_parameters)
        if 'error' in responseJson:
            raise ApiError(responseJson['error']['message'])
        else:
            return AsyncResponse(responseJson)
