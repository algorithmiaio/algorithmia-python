import sys
import os
import json
sys.path = ['../'] + sys.path
import Algorithmia
import six
from Algorithmia.CLI import CLI
import argparse

#bind input to raw input
try:
    input = raw_input
except NameError:
    pass
#CLI app to allow a user to run algorithms and manage data collections

usage = """CLI for interaction with Algorithmia\n
Usage:\n
algo [<cmd>] [options] [<args>...]\n
algo [<cmd>] [--help | --version]\n\n

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
    cat concatenate and print file(s) in a data directory\n\n

  Global options:\n
    --help\n
    --profile <name>\n\n
"""

def main():
    parser = argparse.ArgumentParser('algo', description = "algo [<cmd>] [options] [<args>...] [--help] [--profile]")

    subparsers = parser.add_subparsers(help = 'sub cmd',dest = 'cmd')

    parser_auth = subparsers.add_parser('auth', help = 'save api key and api address for profile')
    parser_auth.add_argument('--profile', action = 'store', type = str, default = 'default')

    parser_clone = subparsers.add_parser('clone', help = 'clone <algo> clone the algorithm repository')
    parser_clone.add_argument('algo')
    parser_clone.add_argument('--profile', action = 'store', type = str, default = 'default')

    #parse options for the run command
    parser_run = subparsers.add_parser('run', help = 'algo run <algo> [input options] <args..> [output options] run an algorithm')

    parser_run.add_argument('algo')
    parser_run.add_argument('-d','--data', action = 'store', help = 'detect input type', default = None)
    parser_run.add_argument('-t','--text', action = 'store', help = 'treat input as text', default = None)
    parser_run.add_argument('-j','--json', action = 'store', help = 'treat input as json data', default = None)
    parser_run.add_argument('-b','--binary', action = 'store', help = 'treat input as binary data', default = None)
    parser_run.add_argument('-D','--data-file', action = 'store', help = 'specify a path to an input file', default = None)
    parser_run.add_argument('-T','--text-file', action = 'store', help = 'specify a path to a text file', default = None)
    parser_run.add_argument('-J','--json-file', action = 'store', help = 'specify a path to a json file', default = None)
    parser_run.add_argument('-B','--binary-file', action = 'store', help = 'specify a path to a binary file', default = None)
    parser_run.add_argument('--timeout', action = 'store',type = int, default = 300, help = 'specify a timeout (seconds)')
    parser_run.add_argument('--debug', action = 'store_true', help = 'print the stdout from the algo <this only works for the owner>')
    parser_run.add_argument('--profile', action = 'store', type = str, default = 'default')
    parser_run.add_argument('-o', '--output', action = 'store', default = None, type = str)

    #subparser for ls
    parser_ls = subparsers.add_parser('ls', help = 'ls [-l] [directory] list the contents of a directory', )

    parser_ls.add_argument('-l', '--long', action = 'store_true')
    parser_ls.add_argument('path', nargs  = '?', default = None)
    parser_ls.add_argument('--profile', action = 'store', type = str, default = 'default')

    #subparser for rm
    parser_rm = subparsers.add_parser('rm', help = 'rm <path> remove a file', )

    parser_rm.add_argument('path', nargs  = '?', default = None)
    parser_rm.add_argument('--profile', action = 'store', type = str, default = 'default')

    #subparser for mkdir
    parser_mkdir = subparsers.add_parser('mkdir', help = 'mkdir <directory> create a directory')

    parser_mkdir.add_argument('path', help = 'directory to create')
    parser_mkdir.add_argument('--profile', action = 'store', type = str, default = 'default')

    #subparser for rmdir
    parser_rmdir = subparsers.add_parser('rmdir', help = 'rmdir [-f] <directory> remove a directory')

    parser_rmdir.add_argument('-f', '--force', action = 'store_true', help = 'force directory removal if it is not empty')
    parser_rmdir.add_argument('path', help = 'directory to remove')
    parser_rmdir.add_argument('--profile', action = 'store', type = str, default = 'default')

    #subparser for cp
    parser_cp = subparsers.add_parser('cp', help = 'cp <src,...> <dest> copy file(s) to the destination',)

    parser_cp.add_argument('src', nargs = '*', type = str, help = 'file(s) to be copied')
    parser_cp.add_argument('dest', help = 'destination for file(s) to be copied to')
    parser_cp.add_argument('--profile', action = 'store', type = str, default = 'default')

    #sub parser for cat
    parser_cat = subparsers.add_parser('cat', help = 'cat <path,...> concatenate and print file(s)')

    parser_cat.add_argument('path', nargs = '*', help = 'file(s) to concatenate and print')
    parser_cat.add_argument('--profile', action = 'store', type = str, default = 'default')

    #sub parser for getting environment template
    parser_template = subparsers.add_parser('template',help='template <envid> <dest> downloads an environment template to the destination')
    parser_template.add_argument('envid',help='environment specification id')
    parser_template.add_argument('dest',help='destination for template download')

    #sub parser for getting environment by language name
    parser_env = subparsers.add_parser('environment', help = 'environment <language> gets environment info by language')
    parser_env.add_argument('language', help='supported language name')


    #sub parser for listing languages
    subparsers.add_parser('languages', help = 'lists supported languages')

    #sub parser for builds
    parser_builds = subparsers.add_parser('builds', help = 'builds <user> <algo> gets build logs for algorithm')
    parser_builds.add_argument('user')
    parser_builds.add_argument('algo',help='algorithm name')

    #sub parser for help

    subparsers.add_parser('help')
    parser.add_argument('--profile', action = 'store', type = str, default = 'default')

    args = parser.parse_args()

    #run auth before trying to create a client
    if args.cmd == 'auth':

        print("Configuring authentication for profile: " + args.profile)

        APIaddress = input("enter API address [https://api.algorithmia.com]: ")
        APIkey = input("enter API key: ")
        CACert = input('(optional) enter path to custom CA certificate: ')

        if len(APIkey) == 28 and APIkey.startswith("sim"):
            if APIaddress == "" or not APIaddress.startswith("https://api."):
                APIaddress = "https://api.algorithmia.com"

            CLI().auth(apikey=APIkey, apiaddress=APIaddress, cacert=CACert, profile=args.profile)
        else:
            print("invalid api key")

    if args.cmd == 'help':
        parser.parse_args(['-h'])

    #create a client with the appropreate api address and key
    client = Algorithmia.client()
    if len(CLI().getAPIaddress(args.profile)) > 1:
        client = Algorithmia.client(CLI().getAPIkey(args.profile), CLI().getAPIaddress(args.profile))
    elif len(CLI().getAPIaddress(args.profile)) > 1 and len(CLI().getCert(args.profile)) > 1:
        client = Algorithmia.client(CLI().getAPIkey(args.profile), CLI().getAPIaddress(args.profile),CLI().getCert(args.profile))
    elif len(CLI().getAPIaddress(args.profile)) < 1 and len(CLI().getCert(args.profile)) > 1:
        client = Algorithmia.client(CLI().getAPIkey(args.profile), CLI().getAPIaddress(args.profile),CLI().getCert(args.profile))
    else:
        client = Algorithmia.client(CLI().getAPIkey(args.profile))

    if args.cmd == 'run':

        print(CLI().runalgo(args, client))

    elif args.cmd == 'clone':

        algo_name = args.algo

        print("cloning src for " + algo_name)

        if CLI().getAPIaddress(args.profile) == None:
            exitcode = os.system("git clone https://git.algorithmia.com/git/"+algo_name+".git")
        else:
            #replace https://api.<domain> with https://git.<domain>
            exitcode = os.system("git clone " + (CLI().getAPIaddress(args.profile).replace("//api.", "//git."))+"/git/"+algo_name+".git")

        if exitcode != 0:
            print("failed to clone\nis git installed?")

    elif args.cmd == 'ls':
        print(CLI().ls(args.path, client, args.long))

    elif args.cmd == 'mkdir':
        CLI().mkdir(args.path, client)

    elif args.cmd == 'rmdir':
        CLI().rmdir(args.path, client, args.force)

    elif args.cmd == 'rm':
        CLI().rm(args.path, client)

    elif args.cmd == 'cp':
        CLI().cp(args.src,args.dest, client)

    elif args.cmd == 'cat':
        print(CLI().cat(args.path, client))
        
    elif args.cmd == 'languages':
        response = CLI().list_languages(client)
        for line in response:
            print(line)

    elif args.cmd == 'template':
        CLI().get_template(args.envid,args.dest,client)

    elif args.cmd == 'environment':
        response = CLI().get_environment_by_language(args.language,client)
        print(response)

    elif args.cmd == 'builds':
        print(CLI().getBuildLogs(args.user, args.algo, client))

    else:
        parser.parse_args(['-h'])






if __name__ == '__main__':
    #main()
    main()