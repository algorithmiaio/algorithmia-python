import sys
import os
import json
import Algorithmia
from pathlib import Path
from Algorithmia.CLI import CLI

import importlib
importlib.reload(Algorithmia.CLI)


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

			CLI().auth(APIkey)

# algo run <algo> <args..>    run the the spesified algo
		elif cmd == 'run':
			algo_name = args[1]

			#if(len(args) > 3):
			algo_input = args[2:]
			#else:
			#	algo_input = args[2:]

			print(algo_input)
			print(len(algo_input))
			print(algo_input[0])
			print(algo_name)
			print(type(algo_name))
			r = CLI().runalgo(algo_name, algo_input, client)
			print(r)
			#print(r.result)

#algo clone <user/algo>
		elif(cmd == "clone"):
			
			algo_name = args[1]

			print("cloning src for" + algo_name)
			exitcode = os.system("git clone https://git.algorithmia.com/git/"+algo_name+".git")

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
				CLI().mkdir(path, client)
			
# algo rmdir <path>
			elif(cmd == "rmdir"):
				CLI().rmdir(path, client)

# algo ls <path>			
			elif(cmd == "ls"):
				print(CLI().ls(path, client))

# algo cat <file>
			elif(cmd == "cat"):
				print(CLI().cat(path, client))

# algo cp <src> <dest>
			elif(cmd == "cp"):

				if(len(args) < 3):
					print("expected algo cp <src> <dest>")
				else:
					src = args[1]
					dest = args[2]

					CLI().cp(src, dest, client)



if __name__ == '__main__':
	main()