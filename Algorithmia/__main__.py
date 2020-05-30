import sys
import os
import Algorithmia

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
	print(args)
	
	if len(args) < 1 or args[0] == "--help":
		print(usage)
	elif args[0] == "--version":
		#print(VERSION)
		print("version")
	else:
		#create a client expecting an apikey to be found in the ALGORITHMIA_API_KEY enviroment variable
		client = Algorithmia.client()
		cmd = args[0]

# algo auth
		if cmd == 'auth':
			#auth
			print("Configuring authentication for 'default' profile")
			APIkey = input("enter API key: ")

			#overwrite apikey enviroment variable
			#os.environ['ALGORITHMIA_API_KEY'] = APIkey
			setenv = "export ALGORITHMIA_API_KEY=" + "'" + APIkey + "'"
			print(setenv)

			# this does not update the enviroment variable properly
			print(os.system(setenv))
			os.system("printenv ALGORITHMIA_API_KEY")

# algo run <algo> <args..>    run the the spesified algo
		elif cmd == 'run':
			#client = Algorithmia.client(os.environ['ALGORITHMIA_API_KEY'])
			algo_name = args[1]

			if(len(args) > 3):
				algo_input = args[2:]
			else:
				algo_input = args[2]

			algo = client.algo(algo_name);
			try:
				print(algo.pipe(algo_input).result)
			except Exception as error:
				print(error)
		else:
			print("in data command")
			#data command
			if(len(args) == 2):
				path = args[1]
			else:
				path = None

# algo mkdir <path>
			if(cmd == "mkdir"):
				#make a dir in data collection
				print("mk "+path)
				newDir = client.dir(path)
				
				if newDir.exists() is False:
					newDir.create()
			
# algo rmdir <path>
			elif(cmd == "rmdir"):
				#remove a dir in data collection
				print("rm "+path)
				Dir = client.dir(path)
				
				if Dir.exists():
					Dir.delete()

# algo ls <path>			
			elif(cmd == "ls"):
				#list dir
				if(path is None):
					path = "/.my"
				print("list "+path)
				listingDir = client.dir(path)
				for f in listingDir.list():
					print(f.getName())

# algo cat <file>
			elif(cmd == "cat"):
				file = client.file(path)
			
				if(file.exists()):
					print(file.getString())
				else:
					print("file does not exist "+path)

# algo cp <src> <dest>
			elif(cmd == "cp"):

				if(len(args) < 3):
					print("expected algo cp <src> <dest>")
				else:
					src = args[1]
					dest = args[2]

					file = client.file(src)
					destLocation = client.file(dest)
					

					if(file.exists()):
						destLocation.putFile(file.getFile())

					else:
						print("file does not exist")




if __name__ == '__main__':
	main()