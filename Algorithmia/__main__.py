import sys
import os
import Algorithmia

#CLI app to allow a user to run algorithms and manage data collections
commands = ['run', 'auth', 'ls', 'mkdir', ]
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
		#match the command
		if cmd == 'auth':
			#auth
			print("Configuring authentication for 'default' profile")
			APIkey = input("enter API key: ")

			#overwrite apikey enviroment variable
			#os.environ['ALGORITHMIA_API_KEY'] = APIkey
			setenv = "export ALGORITHMIA_API_KEY=" + "'" + APIkey + "'"
			print(setenv)
			print(os.system(setenv))
			os.system("printenv ALGORITHMIA_API_KEY")

		#run the spesified algo
		elif cmd == 'run':
			#client = Algorithmia.client(os.environ['ALGORITHMIA_API_KEY'])
			algo_name = args[1]
			algo_input = args[2]

			algo = client.algo(algo_name);
			try:
				print(algo.pipe(algo_input).result)
			except Exception as error:
				print(error)
		else:
			print("in data command")
			#data command
			if(cmd == "mkdir"):
				#make a dir in data collection
				print("mk "+args[2])
			elif(cmd == "ls"):
				#list dir
				print("list "+args[2])




if __name__ == '__main__':
	main()