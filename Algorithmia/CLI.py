import Algorithmia
import os
from Algorithmia.algo_response import AlgoResponse
import json, re, requests
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

		key = open(key, "w")

		toml.dump(config,key)
		key.close()

		print(self.ls(path = None,client = Algorithmia.client(self.getAPIkey(profile))))

	# algo run <algo> <args..>    run the the specified algo
	def runalgo(self, name, inputs, options, client):
		algo_input = inputs

		algo = client.algo(name)
		
		result = None

		algo.set_options(timeout=options.timeout, stdout=options.debug)
		


		#handle input type flags
		if(options.data):
			#data
			algo_input = inputs

			result = algo.pipe(algo_input)

		elif(options.text):
			#text
			key = self.getAPIkey(options.profile)
			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input.encode('utf-8'),
				headers={'Authorization':key,'Content-Type':'text/plain'}, params= algo.query_parameters).json())

		elif(options.json):
			#json
			key = self.getAPIkey(options.profile)
			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input,
				headers={'Authorization':key,'Content-Type':'application/json'}, params= algo.query_parameters).json())
		
		elif(options.binary):
			#binary
			key = self.getAPIkey(options.profile)
			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=bytes(algo_input),
				headers={'Authorization':key,'Content-Type':'application/octet-stream'}, params= algo.query_parameters).json())
		
		elif(options.data_file):
			#data file
			algo_input = open(inputs,"r").read()
			result = algo.pipe(algo_input)

		elif(options.text_file):
			#text file
			algo_input = open(inputs,"r").read()
			key = self.getAPIkey(options.profile)
			
			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input.encode('utf-8'),
				headers={'Authorization':key,'Content-Type':'text/plain'}, params= algo.query_parameters).json())
		
		elif(options.json_file):
			#json file
			#read json file and run algo with that input bypassing the auto detection of input type in pipe
			algo_input = open(inputs,"r").read()
			key = self.getAPIkey(options.profile)

			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=json.dumps(algo_input).encode('utf-8'),
				headers={'Authorization':key,'Content-Type':'application/json'}, params= algo.query_parameters))

		elif(options.binary_file):
			#binary file
			algo_input = open(inputs,"rb").read()
			key = self.getAPIkey(options.profile)

			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=bytes(algo_input),
				headers={'Authorization':key,'Content-Type':'application/octet-stream'}, params= algo.query_parameters).json())

		else:
			result = algo.pipe(algo_input)
		
		#handle output flags

		#response

		#response-body
		if(inputs[-1] == "--response-body"):
			result_body = """{ "result": """+result.result + ",\n" + """  "metadata": """ 
			result_body = result_body + json.dumps(result.metadata.full_metadata)
			result = result_body + " }"

		#output to file if there is an output file spesified
		elif(options.output != None):
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

			except Exception as error:
					print(error)

		return result.result


	# algo mkdir <path>
	def mkdir(self, path, client):
		#make a dir in data collection
		newDir = client.dir(path)
		
		if newDir.exists() is False:
			newDir.create()
				
	# algo rmdir <path>
	def rmdir(self, path, client):
		#remove a dir in data collection

		Dir = client.dir(path)
		
		if Dir.exists():
			Dir.delete()

	def rm(self, path, client):
		
		#for f in path
		file = client.file(path)

		if file.exists():
			file.delete()

	# algo ls <path>			
	def ls(self, path, client, l=False):
		#list dir
		listing = ""
		if(path is None):
			path = "/."

		#listingDir = client.dir(path)
		#for f in listingDir.list():
		#	listing += f.getName() + "\n"

		#long listing
		if(l):
			listingDir = client.dir(path)
			for f in listingDir.list():
				#if(is file)
				listing += f.last_modified.strftime("%Y-%m-%d %H:%M:%S") + '   '
				listing += str(f.size) + '   '
				listing += f.getName() + "\n"
		else:
			listingDir = client.dir(path)
			for f in listingDir.list():
				listing += f.getName() + "\n"

		return listing

	# algo cat <file>
	def cat(self, path, client):
		result = ""
		for f in path:
			file = client.file(f)

			if(file.exists()):
				result += file.getString()
			else:
				result = "file does not exist "+f
				break

		return result

	# algo cp <src> <dest>
	def cp(self, src, dest, client):

		if(src is None or dest is None):
			print("expected algo cp <src> <dest>")
		else:

			
			destLocation = client.file(dest)

			#if src is local and dest is remote
			for f in src:
				if("data://" not in f and "data://" in dest):
					client.file(dest).putFile(f)

				#if src and dest are remote
				elif("data://" in f and "data://" in dest):
					file = client.file(f).getFile()
					filename = file.name
					file.close()
					client.file(dest).putFile(filename)

				#if src is remote and dest is local
				elif("data://" in f and "data://" not in dest):
					file = client.file(f).getFile()
					filename = file.name
					file.close()

					#this assumes dest is a full file path not just a directory
					destFile = open(dest,"w")
					srcfile = open(filename,"r")
					destFile.write(srcfile.read())
					destFile.close()
					srcfile.close()
				else:
					print("at least one of the operands must be a path to a remote data source data://")

	def getconfigfile(self):
		if(os.name == "posix"):
			#if!windows
			#~/.algorithmia/config
			#create the api key file if it does not exist
			keyPath = os.environ['HOME']+"/.algorithmia/"
			keyFile = "config"
			if(not os.path.exists(keyPath)):
				os.mkdir(keyPath)
				file = open(keyPath+keyFile,"w")
				file.write("[profiles]")
				file.close()

			key = keyPath+keyFile
		elif(os.name == "nt"):
			#ifwindows
			#%LOCALAPPDATA%\Algorithmia\config
			#create the api key file if it does not exist
			keyPath = "%LOCALAPPDATA%\\Algorithmia\\"
			keyFile = "config"
			if(not os.path.exists(keyPath)):
				os.mkdir(keyPath)
				file = open(keyPath+keyFile,"w")
				file.write("[profiles]")
				file.close()

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
