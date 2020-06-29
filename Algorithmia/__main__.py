import sys
import os
import json
import Algorithmia
from Algorithmia.CLI import CLI


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
	
	
	if len(args) < 1 or args[0] == "--help":
		print(usage)
	elif args[0] == "--version":
		#print(VERSION)
		print(Algorithmia.version)
	else:

		#create a client with the correct profile
		profile = 'default'
		if(len(args) > 2):
			if(args[-2] == "--profile"):
				profile = args[-1]

		client = Algorithmia.client(CLI().getAPIkey(profile))
		cmd = args[0]

# algo auth
		if cmd == 'auth':
			#auth
			print("Configuring authentication for profile: " + profile)
			APIaddress = input("enter API address:")
			APIkey = input("enter API key: ")

			CLI().auth(APIkey, APIaddress, profile)

# algo run <algo> <args..>    run the the spesified algo
		elif cmd == 'run':
			algo_name = args[1]

			algo_input = args[2:]

			r = CLI().runalgo(algo_name, algo_input, client)
			print(r)

#algo clone <user/algo>
		elif(cmd == "clone"):
			
			algo_name = args[1]

			print("cloning src for" + algo_name)
			#if api address == none
			exitcode = os.system("git clone https://git.algorithmia.com/git/"+algo_name+".git")
			#api address != none
			exitcode = os.system("git clone " + CLI().getAPIaddress(profile)+algo_name+".git")

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