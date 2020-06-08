import sys
import os
import Algorithmia
from pathlib import Path

#CLI app to allow a user to run algorithms and manage data collections

usage = """CLI for interaction with Algorithmia
Usage:
algo [<cmd>] [options] [<args>...]
algo[<cmd>] [--help | --version]

General commands include:
  auth	configure authentication

  Algorithm commands include:
    run	Runs an algorithm
    clone	Clones an algorithm source

  Data commands include:
    ls
    mkdir
    rmdir
    rm
    cp
    cat

  Global options:
    --help
    --profile <name>
"""

def main():
	args = sys.argv[1:]
	#print(args)
	
	if len(args) < 1 or args[0] == "--help":
		print(usage)
	elif args[0] == "--version":
		#print(VERSION)
		print("version")
	else:
		#create the api key file if it does not exist
		keyFile = Path(os.environ['HOME']+"/.algorithmia_api_key")
		keyFile.touch(exist_ok=True)

		#create a client expecting an apikey to be found in the .algorithmia_api_key file
		key = open(os.environ['HOME']+"/.algorithmia_api_key","r")
		client = Algorithmia.client(key.read())
		key.close()
		cmd = args[0]

# algo auth
		if cmd == 'auth':
			#auth
			print("Configuring authentication for 'default' profile")
			APIkey = input("enter API key: ")

			auth(APIkey)

# algo run <algo> <args..>    run the the spesified algo
		elif cmd == 'run':
			algo_name = args[1]

			if(len(args) > 3):
				algo_input = args[2:]
			else:
				algo_input = args[2]

			print(runalgo(algo_name, algo_input, client))
		elif(cmd == "clone"):
			
			algo_name = args[1]

			print("cloning src for" + algo_name)
			exitcode = os.system("git clone https://git.algorithmia.com/git"+algo_name+".git")

			if(exitcode != 0):
				print("failed to clone\nis git installed?")
		else:
			#data command
			if(len(args) == 2):
				path = args[1]
			else:
				path = None

# algo mkdir <path>
			if(cmd == "mkdir"):
				#make a dir in data collection
				mkdir(path, client)
			
# algo rmdir <path>
			elif(cmd == "rmdir"):
				rmdir(path, client)

# algo ls <path>			
			elif(cmd == "ls"):
				print(ls(path, client))

# algo cat <file>
			elif(cmd == "cat"):
				print(cat(path, client))

# algo cp <src> <dest>
			elif(cmd == "cp"):

				if(len(args) < 3):
					print("expected algo cp <src> <dest>")
				else:
					src = args[1]
					dest = args[2]

					cp(src, dest, client)



# algo auth
def auth(apikey):

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
def runalgo(name, inputs, client):
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
def mkdir(path, client):
	#make a dir in data collection
	print("mk "+path)
	newDir = client.dir(path)
	
	if newDir.exists() is False:
		newDir.create()
			
# algo rmdir <path>
def rmdir(path, client):
				#remove a dir in data collection
				print("rm "+path)
				Dir = client.dir(path)
				
				if Dir.exists():
					Dir.delete()

# algo ls <path>			
def ls(path, client):
	#list dir
	listing = ""
	if(path is None):
		path = "/.my"
	print("list "+path)
	listingDir = client.dir(path)
	for f in listingDir.list():
		listing += f.getName() + "\n"
	return listing

# algo cat <file>
def cat(path, client):
	result = None
	file = client.file(path)

	if(file.exists()):
		result = file.getString()
	else:
		result = "file does not exist "+path

	return result

# algo cp <src> <dest>
def cp(src, dest, client):

	if(src is None or dest is None):
		print("expected algo cp <src> <dest>")
	else:

		
		destLocation = client.file(dest)

		#if src is local and dest is remote
		if("data://" not in src and "data://" in dest):
			client.file(dest).putFile(src)

		#if src and dest are remote
		elif("data://" in src and "data://" in dest):
			file = client.file(src).getFile().name
			print(file)
			client.file(dest).putFile(file)

		#if src is remote and dest is local
		elif("data://" in src and "data://" not in dest):
			file = client.file(src).getFile().name
			print(file)

			#this assumes dest is a full file path not just a directory
			destFile = open(dest,"w")
			srcfile = open(file,"r")
			destFile.write(srcfile.read())
			destFile.close()
			srcfile.close()
		else:
			print("at least one of the operands must be a path to a remote data source data://")




if __name__ == '__main__':
	main()