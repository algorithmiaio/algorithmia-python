import Algorithmia
import os
from Algorithmia.algo_response import AlgoResponse
import json, re, requests

class CLI():
	def __init__(self):
		self.client = Algorithmia.client()
		# algo auth
	def auth(self, apikey):

		#setenv = "export ALGORITHMIA_API_KEY=" + "'" + APIkey + "'"
		#print(setenv)

		#store api key in local config file and read from it each time a client needs to be created
		key = open(os.environ['HOME']+"/.algorithmia_api_key","w")
		key.write(apikey)
		key.close()

		print("apikey is:")
		key = open(os.environ['HOME']+"/.algorithmia_api_key","r")
		print(key.read())
		key.close()

	# algo run <algo> <args..>    run the the spesified algo
	def runalgo(self, name, inputs, client):
		algo_name = name

		algo_input = inputs[0]

		algo = client.algo(algo_name)
		
		result = None
		'''
		time = 300
		if("--timeout" in inputs):
			#find timeout value


			time = 300

		algo.set_options(timeout=time, stdout=("--debug" in inputs), output=)
		'''


		#handle input type flags
		if(len(inputs) >= 1):
			if(inputs[0] == "-d" or inputs[0] == "--data"):
				#data
				algo_input = inputs[1]
				print(algo_input)
				try:
					result = algo.pipe(algo_input)
				except Exception as error:
					print(error)

			elif(inputs[0] == '-t'):
				#text
				algo_input = inputs[1]
				key = open(os.environ['HOME']+"/.algorithmia_api_key","r")
				result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input.encode('utf-8'),
					headers={'Authorization':key.read(),'Content-Type':'text/plain'}, params= algo.query_parameters).json())
				key.close()

			elif(inputs[0] == "-j"):
				#json
				algo_input = inputs[1]
				key = open(os.environ['HOME']+"/.algorithmia_api_key","r")
				result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input,
					headers={'Authorization':key.read(),'Content-Type':'application/json'}, params= algo.query_parameters).json())
				key.close()
			
			elif(inputs[0] == "-b"):
				#binary
				algo_input = inputs[1]
				key = open(os.environ['HOME']+"/.algorithmia_api_key","r")
				result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=bytes(algo_input),
					headers={'Authorization':key.read(),'Content-Type':'application/octet-stream'}, params= algo.query_parameters).json())
				key.close()
			
			elif(inputs[0] == "-D" or inputs[0] == "--data-file"):
				#data file
				algo_input = open(inputs[1],"r").read()
				try:
					result = algo.pipe(algo_input)
				except Exception as error:
					print(error)

			elif(inputs[0] == "-T"):
				#text file
				algo_input = open(inputs[1],"r").read()
				key = open(os.environ['HOME']+"/.algorithmia_api_key","r")
				
				result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=algo_input.encode('utf-8'),
					headers={'Authorization':key.read(),'Content-Type':'text/plain'}, params= algo.query_parameters).json())
				key.close()
			
			elif(inputs[0] == "-J"):
				#json file
				#read json file and run algo with that input bypassing the auto detection of input type in pipe
				algo_input = open(inputs[1],"r").read()
				key = open(os.environ['HOME']+"/.algorithmia_api_key","r")

				result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=json.dumps(algo_input).encode('utf-8'),
					headers={'Authorization':key.read(),'Content-Type':'application/json'}, params= algo.query_parameters))
				key.close()

			elif(inputs[0] == "-B"):
				#binary file
				algo_input = open(inputs[1],"rb").read()
				print(algo_input)
				print("end input \n")
				key = open(os.environ['HOME']+"/.algorithmia_api_key","r")

				result = AlgoResponse.create_algo_response(requests.post(client.apiAddress + algo.url, data=bytes(algo_input),
					headers={'Authorization':key.read(),'Content-Type':'application/octet-stream'}, params= algo.query_parameters).json())
				key.close()

			else:
				algo_input = inputs[0]
				try:
					result = algo.pipe(algo_input)
				except Exception as error:
					print(error)
			
			#handle output flags

			#response

		#response-body
		if(inputs[-1] == "--response-body"):
			result_body = """{ "result": """+result.result + ",\n" + """  "metadata": """ 
			result_body = result_body + json.dumps(result.metadata.full_metadata)
			result = result_body + " }"

		#output to file if there is an output file spesified
		elif(len(inputs >= 3)):
			if(inputs[-2] == "--output" or inputs[-2] == "-o"):
				try:
					if isinstance(result.result, bytearray) or isinstance(result.result, bytes):
						out = open(inputs[-1],"wb")
						out.write(result.result)
						out.close()
					else:
						out = open(inputs[-1],"w")
						out.write(result.result)
						out.close()

				except Exception as error:
						print(error)
		else:
			result = result.result

		return result


	# algo mkdir <path>
	def mkdir(self, path, client):
		#make a dir in data collection
		newDir = client.dir(path)
		
		if newDir.exists() is False:
			newDir.create()
				
	# algo rmdir <path>
	def rmdir(self, path, client):
		#remove a dir in data collection
		#print("rm "+path)
		Dir = client.dir(path)
		
		if Dir.exists():
			Dir.delete()

	# algo ls <path>			
	def ls(self, path, client):
		#list dir
		listing = ""
		if(path is None):
			path = "/.my"
		#print("list "+path)
		listingDir = client.dir(path)
		for f in listingDir.list():
			listing += f.getName() + "\n"
		return listing

	# algo cat <file>
	def cat(self, path, client):
		result = None
		file = client.file(path)

		if(file.exists()):
			result = file.getString()
		else:
			result = "file does not exist "+path

		return result

	# algo cp <src> <dest>
	def cp(self, src, dest, client):

		if(src is None or dest is None):
			print("expected algo cp <src> <dest>")
		else:

			
			destLocation = client.file(dest)

			#if src is local and dest is remote
			if("data://" not in src and "data://" in dest):
				client.file(dest).putFile(src)

			#if src and dest are remote
			elif("data://" in src and "data://" in dest):
				file = client.file(src).getFile()
				filename = file.name
				file.close()
				client.file(dest).putFile(filename)

			#if src is remote and dest is local
			elif("data://" in src and "data://" not in dest):
				file = client.file(src).getFile()
				filename = file.name
				file.close()
				#print(file)

				#this assumes dest is a full file path not just a directory
				destFile = open(dest,"w")
				srcfile = open(filename,"r")
				destFile.write(srcfile.read())
				destFile.close()
				srcfile.close()
			else:
				print("at least one of the operands must be a path to a remote data source data://")