import Algorithmia
import os
from Algorithmia.algo_response import AlgoResponse
import json, re, requests, six
import toml


class CLI():
    def __init__(self):
        self.client = Algorithmia.client()
        # algo auth
    def auth(self, apikey, apiaddress, profile):

        #store api key in local config file and read from it each time a client needs to be created
        key = self.getconfigfile()
        config = toml.load(key)

        if('profiles' in config.keys()):
            if(profile in config['profiles'].keys()):
                config['profiles'][profile]['api_key'] = apikey
                config['profiles'][profile]['api_server'] = apiaddress
            else:
                config['profiles'][profile] = {'api_key':apikey,'api_server':apiaddress}
        else:
            config['profiles'] = {profile:{'api_key':apikey,'api_server':apiaddress}}

        with open(key, "w") as key:
            toml.dump(config,key)

        self.ls(path = None,client = Algorithmia.client(self.getAPIkey(profile)))

    # algo run <algo> <args..>    run the the specified algo
    def runalgo(self, options, client):
        algo_input = None

        algo = client.algo(options.algo)
        url = client.apiAddress + algo.url
        result = None
        content = None

        algo.set_options(timeout=options.timeout, stdout=options.debug)

        #handle input type flags
        if(options.data != None):
            #data
            algo_input = options.data

            result = algo.pipe(algo_input)

        elif(options.text != None):
            #text
            algo_input = options.text
            key = self.getAPIkey(options.profile)
            content = 'text/plain'
            algo_input = algo_input.encode('utf-8')

        elif(options.json != None):
            #json
            algo_input = options.json
            key = self.getAPIkey(options.profile)
            content = 'application/json'

        elif(options.binary != None):
            #binary
            algo_input = bytes(options.binary)

            key = self.getAPIkey(options.profile)
            content = 'application/octet-stream'

        elif(options.data_file != None):
            #data file
            algo_input = open(options.data_file,"r").read()
            result = algo.pipe(algo_input)

        elif(options.text_file != None):
            #text file
            algo_input = open(options.text_file,"r").read()
            key = self.getAPIkey(options.profile)
            content = 'text/plain'
            algo_input = algo_input.encode('utf-8')

        elif(options.json_file != None):
            #json file
            #read json file and run algo with that input bypassing the auto detection of input type in pipe
            with open(options.json_file,"r") as f:
                algo_input = f.read()
            key = self.getAPIkey(options.profile)
            content = 'application/json'
            algo_input = json.dumps(algo_input).encode('utf-8')


        elif(options.binary_file != None):
            #binary file
            with open(options.binary_file,"rb") as f:
                algo_inputs = bytes(f.read())
            key = self.getAPIkey(options.profile)
            content = 'application/octet-stream'


        else:
            output = "no valid input detected"

        if(content != None):
            result = AlgoResponse.create_algo_response(requests.post(url, data=algo_input,
                    headers={'Authorization':key,'Content-Type':content}, params= algo.query_parameters).json())

        if(result != None):
            output = result.result

        #handle output flags

        #output to file if there is an output file specified
        if(options.output != None):
            outputFile = options.output
            try:
                if isinstance(result.result, bytearray) or isinstance(result.result, bytes):
                    out = open(outputFile,"wb")
                    out.write(result.result)
                    out.close()
                else:
                    out = open(outputFile,"w")
                    out.write(result.result)
                    out.close()
                output = ""

            except Exception as error:
                print(error)

        return output


    # algo mkdir <path>
    def mkdir(self, path, client):
        #make a dir in data collection
        newDir = client.dir(path)

        if newDir.exists() is False:
            newDir.create()

    # algo rmdir <path>
    def rmdir(self, path, client, force = False):
        #remove a dir in data collection

        Dir = client.dir(path)

        try:
            if Dir.exists():
                Dir.delete(force)
        except Algorithmia.errors.DataApiError as e:
            print(e)


    def rm(self, path, client):

        #for f in path
        file = client.file(path)
        try:
            if file.exists():
                file.delete()
        except Algorithmia.errors.DataApiError as e:
            print(e)

    # algo ls <path>
    def ls(self, path, client, l=False):
        #list dir
        listing = ""
        if(path is None):
            path = "data://"

        if('data://' in path):
            file = path.split('/')
            if(len(file) == 5 and file[-1] != ''):
                #path is a file
                directory = path[:-len(file[-1])]
                f = client.dir(directory)
                #get directory iterate files listing+=file if(filename == file[-1])

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
                        if(file_info['filename'] == file[-1]):
                            f.set_attributes(file_info)

                if(l):
                    listing += f.last_modified.strftime("%Y-%m-%d %H:%M:%S") + '   '
                    listing += str(f.size) + '   '
                    listing += 'data://'+f.path + "\n"
                else:
                    listing += 'data://'+f.path + "\n"
            else:
                #path is a directory
                #long listing
                if(l):

                    listingDir = client.dir(path)
                    for f in listingDir.files():
                        listing += f.last_modified.strftime("%Y-%m-%d %H:%M:%S") + '   '
                        listing += str(f.size) + '   '
                        listing += 'data://'+f.path + "\n"
                    for f in listingDir.dirs():
                        listing += 'data://'+f.path + "\n"

                else:
                    listingDir = client.dir(path)
                    for f in listingDir.list():
                        listing += 'data://'+f.path + "\n"
        else:
            print("operand must be a path to a remote data source data://")

        return listing

    # algo cat <file>
    def cat(self, path, client):
        result = ""
        for f in path:
            if('data://' in f):
                if(f[-1] == '*'):
                    path += ['data://'+file.path for file in client.dir(f[:len(f)-2]).files()]
                else:
                    file = client.file(f)

                    if(file.exists()):
                        result += file.getString()
                    else:
                        result = "file does not exist "+f
                        break
            else:
                print("operands must be a path to a remote data source data://")
                break

        return result

    # algo cp <src> <dest>
    def cp(self, src, dest, client):

        if(src is None or dest is None):
            print("expected algo cp <src> <dest>")
        else:

            destLocation = client.file(dest)
            for f in src:


                #if dest is a directory apend the src name
                #if there are multiple src files only the final one will be copied if dest is not a directory
                destPath = dest

                path = dest.split('/')
                print(path)

                if(os.path.isdir(dest) or client.dir(dest).exists() and len(path) <= 5):
                    if(dest[-1] == '/' and path[-1] == ''):
                        destPath+=client.file(f).getName()
                    elif(len(path) == 4 or "data://" not in dest):
                        destPath+='/'+client.file(f).getName()

                if(f[-1] == '*'):
                    src += ['data://'+file.path for file in client.dir(f[:len(f)-2]).files()]

                #if src is local and dest is remote
                elif("data://" not in f and "data://" in dest):
                    client.file(destPath).putFile(f)

                #if src and dest are remote
                elif("data://" in f and "data://" in dest):
                    file = client.file(f).getFile()
                    filename = file.name
                    file.close()

                    client.file(destPath).putFile(filename)

                #if src is remote and dest is local
                elif("data://" in f and "data://" not in dest):
                    file = client.file(f).getFile()
                    filename = file.name
                    file.close()
                    os.system("mv " + filename + " " + destPath)
                else:
                    print("at least one of the operands must be a path to a remote data source data://")

    def getconfigfile(self):
        if(os.name == "posix"):
            #if!windows
            #~/.algorithmia/config
            #create the api key file if it does not exist
            keyPath = os.environ['HOME']+"/.algorithmia/"

        elif(os.name == "nt"):
            #ifwindows
            #%LOCALAPPDATA%\Algorithmia\config
            #create the api key file if it does not exist
            keyPath = "%LOCALAPPDATA%\\Algorithmia\\"
        
        keyFile = "config"

        if(not os.path.exists(keyPath)):
            os.mkdir(keyPath)

        if(not os.path.exists(keyPath+keyFile)):
            with open(keyPath+keyFile,"w") as file:
                file.write("[profiles]\n")
                file.write("[profiles.default]\n")
                file.write("api_key = ''\n")
                file.write("api_server = ''\n")


        key = keyPath+keyFile

        return key

    def getAPIkey(self,profile):
        key = self.getconfigfile()
        config_dict = toml.load(key)
        apikey = None
        if('profiles' in config_dict.keys() and profile in config_dict['profiles'].keys()):
            apikey = config_dict['profiles'][profile]['api_key']
        return apikey

    def getAPIaddress(self,profile):
        key = self.getconfigfile()
        config_dict = toml.load(key)

        apiaddress = config_dict['profiles'][profile]['api_server']

        return apiaddress
