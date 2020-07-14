import sys
import os
import json
import Algorithmia
from Algorithmia.CLI import CLI
import argparse


#CLI app to allow a user to run algorithms and manage data collections

usage = """CLI for interaction with Algorithmia\n
Usage:\n
algo [<cmd>] [options] [<args>...]\n
algo[<cmd>] [--help | --version]\n\n

General commands include:\n
  auth	configure authentication\n\n

  Algorithm commands include:\n
    run	Runs an algorithm\n
    clone	Clones an algorithm source\n\n

  Data commands include:\n
    ls list the contents of a data directory\n
    mkdir create a data directory\n
    rmdir remove a data directory\n
    rm remove a file from a data directory\n
    cp copy file(s) to or from a data directory\n
    cat concatinate and print file(s) in a data directory\n\n

  Global options:\n
    --help\n
    --profile <name>\n\n
"""

def main():
	parser = argparse.ArgumentParser('algo', description = usage)

	subparsers = parser.add_subparsers(help = 'sub cmd',dest = 'cmd')

	parser_auth = subparsers.add_parser('auth', help = 'save api key and api address for profile')
	parser_auth.add_argument('--profile', action = 'store', type = str, default = 'default')

	parser_clone = subparsers.add_parser('clone', help = 'clone <algo>')
	parser_clone.add_argument('algo')
	parser_clone.add_argument('--profile', action = 'store', type = str, default = 'default')

	#parse options for the run command
	parser_run = subparsers.add_parser('run', help = 'algo run <algo> [input options] <args..> [output options]')

	parser_run.add_argument('algo')
	parser_run.add_argument('-d','--data', action = 'store_true', help = 'detect input type')
	parser_run.add_argument('-t','--text', action = 'store_true', help = 'treat input as text')
	parser_run.add_argument('-j','--json', action = 'store_true', help = 'treat input as json data')
	parser_run.add_argument('-b','--binary', action = 'store_true', help = 'treat input as binary data')
	parser_run.add_argument('-D','--data-file', action = 'store_true', help = 'spesify a path to an input file')
	parser_run.add_argument('-T','--text-file', action = 'store_true', help = 'spesify a path to a text file')
	parser_run.add_argument('-J','--json-file', action = 'store_true', help = 'spesify a path to a json file')
	parser_run.add_argument('-B','--binary-file', action = 'store_true', help = 'spesify a path to a binary file')
	parser_run.add_argument('input')
	parser_run.add_argument('--timeout', action = 'store',type = int, default = 300, help = 'spesify a timeout')
	parser_run.add_argument('--debug', action = 'store_true', help = 'print the stdout from the algo <this only works for the owner>')
	parser_run.add_argument('--profile', action = 'store', type = str, default = 'default')
	parser_run.add_argument('-o', '--output', action = 'store', default = None, type = str)

	#subparser for ls
	parser_ls = subparsers.add_parser('ls', help = 'ls [-l] [directory]', )
	
	parser_ls.add_argument('-l', action = 'store_true')
	parser_ls.add_argument('path', nargs  = '?', default = None)
	parser_ls.add_argument('--profile', action = 'store', type = str, default = 'default')

	#subparser for rm
	parser_rm = subparsers.add_parser('rm', help = 'rm <path>', )
	
	parser_rm.add_argument('path', nargs  = '?', default = None)
	parser_rm.add_argument('--profile', action = 'store', type = str, default = 'default')

	#subparser for mkdir
	parser_mkdir = subparsers.add_parser('mkdir', help = 'mkdir <directory>')
	
	parser_mkdir.add_argument('path', help = 'directory to create')
	parser_mkdir.add_argument('--profile', action = 'store', type = str, default = 'default')

	#subparser for rmdir
	parser_rmdir = subparsers.add_parser('rmdir', help = 'rmdir [-f] <directory>')
	
	parser_rmdir.add_argument('-f', action = 'store_true', help = 'force directory removal if it is not empty')
	parser_rmdir.add_argument('path', help = 'directory to remove')
	parser_rmdir.add_argument('--profile', action = 'store', type = str, default = 'default')

	#subparser for cp
	parser_cp = subparsers.add_parser('cp', help = 'cp <src,...> <dest>',)
	
	parser_cp.add_argument('src', nargs = '*', type = str, help = 'file(s) to be coppied')
	parser_cp.add_argument('dest', help = 'destination for file(s) to be coppied to')
	parser_cp.add_argument('--profile', action = 'store', type = str, default = 'default')

	#sub parser for cat
	parser_cat = subparsers.add_parser('cat', help = 'cat <path,...>')
	
	parser_cat.add_argument('path', nargs = '*', help = 'file(s) to concatinate and print')
	parser_cat.add_argument('--profile', action = 'store', type = str, default = 'default')

	subparsers.add_parser('help')
	parser.add_argument('--profile', action = 'store', type = str, default = 'default')

	args = parser.parse_args()

	#run auth before trying to create a client
	if(args.cmd == 'auth'):

		print("Configuring authentication for profile: " + args.profile)
		APIaddress = input("enter API address:")
		APIkey = input("enter API key:")

		if(len(APIkey) == 28 and APIkey.startswith("sim")):
			CLI().auth(APIkey, APIaddress, args.profile)
		else:
			print("invalid api key")

	if(args.cmd == 'help'):
		parser.parse_args(['-h'])

	#create a client with the appropreate api address and key
	client = Algorithmia.client()
	if(len(CLI().getAPIaddress(args.profile)) > 1):
		client = Algorithmia.client(CLI().getAPIkey(args.profile), CLI().getAPIaddress(args.profile))
	else:
		client = Algorithmia.client(CLI().getAPIkey(args.profile))
	
	
	if(args.cmd == 'run'):

		algo_name = args.algo

		algo_input = args.input

		print(CLI().runalgo(algo_name, algo_input, args, client))

	elif(args.cmd == 'clone'):

		algo_name = args.algo

		print("cloning src for" + algo_name)
		if(CLI().getAPIaddress(profile) == None):
			exitcode = os.system("git clone https://git.algorithmia.com/git/"+algo_name+".git")
		else:
			#replace https://api.<domain> with https://git.<domain>
			exitcode = os.system("git clone " + (CLI().getAPIaddress(profile).replace("//api.", "//git."))+"/git/"+algo_name+".git")

		if(exitcode != 0):
			print("failed to clone\nis git installed?")
	
	if(args.cmd == 'ls'):
		print(CLI().ls(args.path, client, args.l))
	
	elif(args.cmd == 'mkdir'):
		CLI().mkdir(args.path, client)

	elif(args.cmd == 'rmdir'):
		CLI().rmdir(args.path, client)

	elif(args.cmd == 'rm'):
		CLI().rm(args.path, client)
	
	elif(args.cmd == 'cp'):
		print(CLI().cp(args.src,args.dest, client))

	elif(args.cmd == 'cat'):
		print(CLI().cat(args.path, client))






if __name__ == '__main__':
	#main()
	main()