'Algorithmia Algorithm API Client (python)'

import base64
import json
import re
from Algorithmia.async_response import AsyncResponse
from Algorithmia.algo_response import AlgoResponse
from Algorithmia.errors import ApiError, ApiInternalError
from enum import Enum
from algorithmia_api_client.rest import ApiException
from algorithmia_api_client import CreateRequest, UpdateRequest, VersionRequest, Details, Settings, SettingsMandatory, SettingsPublish, \
    CreateRequestVersionInfo, VersionInfo, VersionInfoPublish

OutputType = Enum('OutputType','default raw void')

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
        self.query_parameters = {'timeout':timeout, 'stdout':stdout}
        self.output_type = output
        self.query_parameters.update(query_parameters)
        return self

    # Create a new algorithm
    def create(self, details={}, settings={}, version_info={}):
        detailsObj = Details(**details)
        settingsObj = SettingsMandatory(**settings)
        createRequestVersionInfoObj = CreateRequestVersionInfo(**version_info)
        create_parameters = {"name": self.algoname, "details": detailsObj, "settings": settingsObj, "version_info": createRequestVersionInfoObj}
        create_request = CreateRequest(**create_parameters)
        try:
            # Create Algorithm
            api_response = self.client.manageApi.create_algorithm(self.username, create_request)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)

    # Update the settings in an algorithm
    def update(self, details={}, settings={}, version_info={}):
        detailsObj = Details(**details)
        settingsObj = Settings(**settings)
        createRequestVersionInfoObj = CreateRequestVersionInfo(**version_info)
        update_parameters = {"details": detailsObj, "settings": settingsObj, "version_info": createRequestVersionInfoObj}
        update_request = UpdateRequest(**update_parameters)
        try:
            # Update Algorithm
            api_response = self.client.manageApi.update_algorithm(self.username, self.algoname, update_request)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)

    # Publish an algorithm
    def publish(self, details={}, settings={}, version_info={}):
        detailsObj = Details(**details)
        settingsObj = SettingsPublish(**settings)
        versionRequestObj = VersionInfoPublish(**version_info)
        publish_parameters = {"details": detailsObj, "settings": settingsObj, "version_info": versionRequestObj}
        version_request = VersionRequest(**publish_parameters) # VersionRequest | Publish Version Request
        try:
            # Publish Algorithm
            api_response = self.client.manageApi.publish_algorithm(self.username, self.algoname, version_request)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)

    def builds(self, limit=56, marker=None):
        try:
            if marker is not None:
                api_response = self.client.manageApi.get_algorithm_builds(self.username, self.algoname, limit=limit, marker=marker)
            else:
                api_response = self.client.manageApi.get_algorithm_builds(self.username, self.algoname, limit=limit)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)

    def get_build(self, build_id):
        # Get the build object for a given build_id
        # The build status can have one of the following value: succeeded, failed, in-progress
        try:
            api_response = self.client.manageApi.get_algorithm_build_by_id(self.username, self.algoname, build_id)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)

    def get_build_logs(self, build_id):
        # Get the algorithm build logs for a given build_id
        try:
            api_response = self.client.manageApi.get_algorithm_build_logs(self.username, self.algoname, build_id)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)

    # Get info on an algorithm
    def info(self, algo_hash=None):
        try:
            # Get Algorithm
            if algo_hash:
                api_response = self.client.manageApi.get_algorithm_hash_version(self.username, self.algoname, algo_hash)
            else:
                api_response = self.client.manageApi.get_algorithm(self.username, self.algoname)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)

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
        try:
            # Get Algorithm versions
            api_response = self.client.manageApi.get_algorithm_versions(self.username, self.algoname, **kwargs)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)


    # Compile an algorithm
    def compile(self):
        try:
            # Compile algorithm
            api_response = self.client.manageApi.algorithms_username_algoname_compile_post(self.username, self.algoname)
            return api_response
        except ApiException as e:
            error_message = json.loads(e.body)["error"]["message"]
            raise ApiError(error_message)

    # Pipe an input into this algorithm
    def pipe(self, input1):

        if self.output_type == OutputType.raw:
            return self._postRawOutput(input1)
        elif self.output_type == OutputType.void:
            return self._postVoidOutput(input1)
        else:
            return AlgoResponse.create_algo_response(self.client.postJsonHelper(self.url, input1, **self.query_parameters))

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
