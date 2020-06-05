import Algorithmia
import os

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
		#client = Algorithmia.client(os.environ['ALGORITHMIA_API_KEY'])
		algo_name = name

		algo_input = inputs

		result = None

		algo = client.algo(algo_name);
		try:
			result = algo.pipe(algo_input).result
		except Exception as error:
			print(error)

		return result



	# algo mkdir <path>
	def mkdir(self, path, client):
		#make a dir in data collection
		#print("mk "+path)
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