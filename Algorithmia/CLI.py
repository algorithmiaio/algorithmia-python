import Algorithmia
import os
from Algorithmia.errors import DataApiError, AlgorithmException
from Algorithmia.algo_response import AlgoResponse
import json, re, requests, six
import toml
import shutil

class CLI:
    def __init__(self):
        self.client = Algorithmia.client()
        # algo auth
    def auth(self, apiaddress, apikey="", cacert="", profile="default", bearer=""):

        # store api key in local config file and read from it each time a client needs to be created
        key = self.getconfigfile()
        config = toml.load(key)

        if ('profiles' in config.keys()):
            if (profile in config['profiles'].keys()):
                config['profiles'][profile]['api_key'] = apikey
                config['profiles'][profile]['api_server'] = apiaddress
                config['profiles'][profile]['ca_cert'] = cacert
                config['profiles'][profile]['bearer_token'] = bearer

            else:
                config['profiles'][profile] = {'api_key':apikey,'api_server':apiaddress,'ca_cert':cacert,'bearer_token':bearer}
        else:
            config['profiles'] = {profile:{'api_key':apikey,'api_server':apiaddress,'ca_cert':cacert,'bearer_token':bearer }}

        with open(key, "w") as key:
            toml.dump(config,key)

        self.ls(path = None,client = CLI().getClient(profile))

    # algo run <algo> <args..>    run the the specified algo
    def runalgo(self, options, client):
        algo_input = None

        algo = client.algo(options.algo)
        url = client.apiAddress + algo.url
        result = None
        content = None

        algo.set_options(timeout=options.timeout, stdout=options.debug)

        # handle input type flags
        if (options.data != None):
            # data
            algo_input = options.data

            result = algo.pipe(algo_input)

        elif (options.text != None):
            # text
            algo_input = options.text
            key = self.getAPIkey(options.profile)
            content = 'text/plain'
            algo_input = algo_input.encode('utf-8')

        elif (options.json != None):
            # json
            algo_input = options.json
            key = self.getAPIkey(options.profile)
            content = 'application/json'

        elif (options.binary != None):
            # binary
            algo_input = bytes(options.binary)

            key = self.getAPIkey(options.profile)
            content = 'application/octet-stream'

        elif (options.data_file != None):
            # data file
            algo_input = open(options.data_file, "r").read()
            result = algo.pipe(algo_input)

        elif (options.text_file != None):
            # text file
            algo_input = open(options.text_file, "r").read()
            key = self.getAPIkey(options.profile)
            content = 'text/plain'
            algo_input = algo_input.encode('utf-8')

        elif (options.json_file != None):
            # json file
            # read json file and run algo with that input bypassing the auto detection of input type in pipe
            with open(options.json_file, "r") as f:
                algo_input = f.read()
            key = self.getAPIkey(options.profile)
            content = 'application/json'
            algo_input = json.dumps(algo_input).encode('utf-8')


        elif (options.binary_file != None):
            # binary file
            with open(options.binary_file, "rb") as f:
                algo_input = bytes(f.read())
            key = self.getAPIkey(options.profile)
            content = 'application/octet-stream'


        else:
            output = "no valid input detected"

        if (content != None):
            result = AlgoResponse.create_algo_response(requests.post(url, data=algo_input,
                                                                     headers={'Authorization': key,
                                                                              'Content-Type': content},
                                                                     params=algo.query_parameters).json())

        if (result != None):
            output = result.result

        # handle output flags

        # output to file if there is an output file specified
        if (options.output != None):
            outputFile = options.output
            try:
                if isinstance(result.result, bytearray) or isinstance(result.result, bytes):
                    out = open(outputFile, "wb")
                    out.write(result.result)
                    out.close()
                else:
                    out = open(outputFile, "w")
                    out.write(result.result)
                    out.close()
                output = ""

            except Exception as error:
                print(error)

        return output

    # algo mkdir <path>
    def mkdir(self, path, client):
        # make a dir in data collection
        newDir = client.dir(path)

        if newDir.exists() is False:
            newDir.create()

    # algo rmdir <path>
    def rmdir(self, path, client, force=False):
        # remove a dir in data collection

        Dir = client.dir(path)

        try:
            if Dir.exists():
                Dir.delete(force)
        except Algorithmia.errors.DataApiError as e:
            print(e)

    def rm(self, path, client):

        # for f in path
        file = client.file(path)
        try:
            if file.exists():
                file.delete()
        except Algorithmia.errors.DataApiError as e:
            print(e)

    # algo ls <path>
    def ls(self, path, client, longlist=False):
        # by default list user's hosted data
        listing = ""
        if path is None:
            path = "data://"

        file = path.split('/')
        if file[-1] != '':
            # path is a file, list parent
            directory = path[:-len(file[-1])]
            f = client.dir(directory)

            response = client.getHelper(f.url, **{})
            if response.status_code != 200:
                raise DataApiError("failed to get file info: " + str(response.content))

            responseContent = response.content
            if isinstance(responseContent, six.binary_type):
                responseContent = responseContent.decode()

            content = json.loads(responseContent)

            if 'files' in content:
                f = client.file(path)
                for file_info in content['files']:
                    if file_info['filename'] == file[-1]:
                        f.set_attributes(file_info)

            if longlist:
                listing += f.last_modified.strftime("%Y-%m-%d %H:%M:%S") + '   '
                listing += str(f.size) + '   '
                listing += f.path + "\n"
            else:
                listing += f.path + "\n"
        else:
            # path is a directory
            if longlist:
                listingDir = client.dir(path)
                for f in listingDir.dirs():
                    listing += f.path + "/\n"
                for f in listingDir.files():
                    listing += f.last_modified.strftime("%Y-%m-%d %H:%M:%S") + '   '
                    listing += str(f.size) + '   '
                    listing += f.path + "\n"

            else:
                listingDir = client.dir(path)
                for f in listingDir.dirs():
                    listing += f.path + "/\n"
                for f in listingDir.files():
                    listing += f.path + "\n"

        return listing

    # algo cat <file>
    def cat(self, path, client):
        result = ""
        for f in path:
            if '://' in f and not f.startswith("http"):
                if f[-1] == '*':
                    path += ['data://' + file.path for file in client.dir(f[:len(f) - 2]).files()]
                else:
                    file = client.file(f)

                    if file.exists():
                        result += file.getString()
                    else:
                        result = "file does not exist " + f
                        break
            else:
                print("operands must be a path to a remote data source data://")
                break

        return result

    # algo freeze
    def freezeAlgo(self, client, manifest_path="model_manifest.json"):
        client.freeze(manifest_path)

    # algo cp <src> <dest>
    def cp(self, src, dest, client):

        if (src is None or dest is None):
            print("expected algo cp <src> <dest>")
        else:

            destLocation = client.file(dest)
            for f in src:

                # if dest is a directory apend the src name
                # if there are multiple src files only the final one will be copied if dest is not a directory
                destPath = dest

                path = dest.split('/')

                if (os.path.isdir(dest) or client.dir(dest).exists() and len(path) <= 5):
                    if (dest[-1] == '/' and path[-1] == ''):
                        destPath += client.file(f).getName()
                    elif (len(path) == 4 or "data://" not in dest):
                        destPath += '/' + client.file(f).getName()

                if (f[-1] == '*'):
                    src += ['data://' + file.path for file in client.dir(f[:len(f) - 2]).files()]

                # if src is local and dest is remote
                elif ("data://" not in f and "data://" in dest):
                    client.file(destPath).putFile(f)

                # if src and dest are remote
                elif ("data://" in f and "data://" in dest):
                    file = client.file(f).getFile()
                    filename = file.name
                    file.close()

                    client.file(destPath).putFile(filename)

                # if src is remote and dest is local
                elif ("data://" in f and "data://" not in dest):
                    file = client.file(f).getFile()
                    filename = file.name
                    file.close()
                    shutil.move(filename, destPath)
                else:
                    print("at least one of the operands must be a path to a remote data source data://")

    def get_environment_by_language(self, language, client):
        response = client.get_environment(language)
        if "error" in response:
            return json.dumps(response)
        return json.dumps(response['environments'], indent=1)

    def list_languages(self, client):
        response = client.get_supported_languages()
        table = []
        if "error" not in response:
            table.append("{:<25} {:<35}".format('Name', 'Description'))
            for lang in response:
                table.append("{:<25} {:<35}".format(lang['name'], lang['display_name']))
        else:
            table.append(json.dumps(response))
        return table

    def getBuildLogs(self, user, algo, client):
        api_response = client.algo(user + '/' + algo).get_builds()
        return json.dumps(api_response['results'], indent=1)


    def getconfigfile(self):
        if (os.name == "posix"):
            # if!windows
            # ~/.algorithmia/config
            # create the api key file if it does not exist
            keyPath = os.environ['HOME'] + "/.algorithmia/"

        elif (os.name == "nt"):
            # ifwindows
            # %LOCALAPPDATA%\Algorithmia\config
            # create the api key file if it does not exist
            keyPath = os.path.expandvars("%LOCALAPPDATA%\\Algorithmia\\")

        keyFile = "config"

        if (not os.path.exists(keyPath)):
            os.mkdir(keyPath)

        if (not os.path.exists(keyPath + keyFile)):
            with open(keyPath + keyFile, "w") as file:
                file.write("[profiles]\n")
                file.write("[profiles.default]\n")
                file.write("api_key = ''\n")
                file.write("api_server = ''\n")
                file.write("ca_cert = ''\n")
                file.write("bearer_token = ''\n")

        key = keyPath + keyFile

        return key

    def get_template(self, envid, dest, client):
        response = client.get_template(envid, dest)
        return response

    def getAPIkey(self, profile):
        key = self.getconfigfile()
        config_dict = toml.load(key)
        if 'profiles' in config_dict and profile in config_dict['profiles'] and \
                config_dict['profiles'][profile]['api_key'] != "":
            return config_dict['profiles'][profile]['api_key']
        else:
            return None
    
    def getBearerToken(self,profile):
        key = self.getconfigfile()
        config_dict = toml.load(key)
        if 'profiles' in config_dict and profile in config_dict['profiles'] and \
                config_dict['profiles'][profile]['bearer_token'] != "":
            return config_dict['profiles'][profile]['bearer_token']
        else:
            return None


    def getAPIaddress(self, profile):
        key = self.getconfigfile()
        config_dict = toml.load(key)

        if config_dict['profiles'][profile]['api_server'] != "":
            return config_dict['profiles'][profile]['api_server']
        else:
            return None

    def getCert(self, profile):
        key = self.getconfigfile()
        config_dict = toml.load(key)
        if 'profiles' in config_dict and profile in config_dict['profiles'] and \
                config_dict['profiles'][profile]['ca_cert'] != "":
            return config_dict['profiles'][profile]['ca_cert']
        else:
            return None

    def getClient(self,profile):
        apiAddress = self.getAPIaddress(profile)
        apiKey = self.getAPIkey(profile)
        caCert = self.getCert(profile)
        bearer = None

        if apiKey is None:
            bearer = self.getBearerToken(profile)

        return Algorithmia.client(api_key=apiKey,api_address=apiAddress,ca_cert=caCert,bearer_token = bearer)
