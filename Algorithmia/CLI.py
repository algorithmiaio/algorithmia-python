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

		self.ls(path = None,client = Algorithmia.client(self.getAPIkey(profile)))

	# algo run <algo> <args..>    run the the specified algo
	def runalgo(self, options, client):
		algo_input = None

		algo = client.algo(options.algo)
		
		result = None

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
			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input.encode('utf-8'),
				headers={'Authorization':key,'Content-Type':'text/plain'}, params= algo.query_parameters).json())

		elif(options.json != None):
			#json
			algo_input = options.json
			key = self.getAPIkey(options.profile)
			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input,
				headers={'Authorization':key,'Content-Type':'application/json'}, params= algo.query_parameters).json())
		
		elif(options.binary != None):
			#binary
			algo_input = options.binary
			key = self.getAPIkey(options.profile)
			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=bytes(algo_input),
				headers={'Authorization':key,'Content-Type':'application/octet-stream'}, params= algo.query_parameters).json())
		
		elif(options.data_file != None):
			#data file
			algo_input = open(options.data_file,"r").read()
			result = algo.pipe(algo_input)

		elif(options.text_file != None):
			#text file
			algo_input = open(options.text_file,"r").read()
			key = self.getAPIkey(options.profile)
			
			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input.encode('utf-8'),
				headers={'Authorization':key,'Content-Type':'text/plain'}, params= algo.query_parameters).json())
		
		elif(options.json_file != None):
			#json file
			#read json file and run algo with that input bypassing the auto detection of input type in pipe
			algo_input = open(options.json_file,"r").read()
			key = self.getAPIkey(options.profile)

			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=json.dumps(algo_input).encode('utf-8'),
				headers={'Authorization':key,'Content-Type':'application/json'}, params= algo.query_parameters))

		elif(options.binary_file != None):
			#binary file
			algo_input = open(options.binary_file,"rb").read()
			key = self.getAPIkey(options.profile)

			result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=bytes(algo_input),
				headers={'Authorization':key,'Content-Type':'application/octet-stream'}, params= algo.query_parameters).json())

		else:
			output = "no valid input detected"

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
		
		if Dir.exists():
			Dir.delete(force)


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
			path = "data://"

		if('data://' in path):
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
				if(os.path.isdir(dest) or client.dir(dest).exists()):
					if(dest[-1] == '/'):
						destPath+=client.file(f).getName()
					else:
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
