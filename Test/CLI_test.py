import sys
# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest
import os
import Algorithmia
from Algorithmia.CLI import CLI

class CLITest(unittest.TestCase):
	def setUp(self):
		# create a directory to use in testing the cp command 
		client = Algorithmia.client('')
		CLI().mkdir("/.my/moredata", client)
	
	def test_ls(self):
		parentDir = "/.my/"
		newDir = "test"
		client = Algorithmia.client()

		CLI().mkdir(parentDir+newDir, client)
		result = CLI().ls(parentDir, client)
		self.assertTrue(result is not None and "moredata" in result and newDir in result)
		
		CLI().rmdir(parentDir+newDir, client)


	def test_mkdir(self):

		parentDir = "/.my/"
		newDir = "test"
		client = Algorithmia.client('simdylfCeXZ8/MgaQzokUHlalWm1')

		CLI().mkdir(parentDir+newDir, client)
		result = CLI().ls(parentDir, client)
		self.assertTrue(newDir in result)
		
		CLI().rmdir(parentDir+newDir, client)

	def test_rmdir(self):
		parentDir = "/.my/"
		newDir = "testRmdir"
		client = Algorithmia.client()

		CLI().mkdir(parentDir+newDir, client)
		result = CLI().ls(parentDir, client)
		self.assertTrue(newDir in result)
		
		CLI().rmdir(parentDir+newDir, client)

		result = CLI().ls(parentDir, client)
		self.assertTrue(newDir not in result)

	def test_cat(self):
		file = "data://.my/moredata/test.txt"
		fileContents = "some text in test file"
		client = Algorithmia.client()

		CLI().rm(file, client)
		testfile = open("./test.txt", "w")
		testfile.write(fileContents)
		testfile.close()

		CLI().cp("./test.txt",file,client)

		result = CLI().cat(file,client)
		self.assertEqual(result, fileContents)


#local to remote
	def test_cp_L2R(self):
		client = Algorithmia.client()

		testfile = open("./test.txt", "w")
		testfile.write("some text")
		testfile.close()

		src = "./test.txt"
		dest = "data://.my/moredata/test.txt"
		CLI().cp(src,dest,client)

		result = CLI().ls("/.my/moredata/",client)
		self.assertTrue("test.txt" in result)

#remote to remote
	def test_cp_R2R(self):
		client = Algorithmia.client()

		src = "data://.my/moredata/test.txt"
		dest = "data://.my/moredata/test2.txt"
		CLI().cp(src,dest,client)

		result = CLI().ls("/.my/moredata",client)
		self.assertTrue("test2.txt" in result)

#remote to local
	def test_cp_R2L(self):
		src = "data://.my/moredata/test.txt"
		dest = "./test.txt"
		client = Algorithmia.client()

		CLI().cp(src,dest,client)
		self.assertTrue(os.path.isfile(dest))

	def test_run(self):
		name = "util/Echo"
		inputs = "test"
		client = Algorithmia.client()

		parser = argparse.ArgumentParser('CLI for interacting with Algorithmia', description = usage)

		subparsers = parser.add_subparsers(help = 'sub cmd',dest = 'subparser_name')
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
		
		args = parser.parse_args(['run',name,'-d',inputs])

		result = CLI().runalgo(name,inputs, args, client)
		self.assertEqual(result, inputs[0])
	
	def test_auth(self):
		#key for test account
		key = "simdylfCeXZ8/MgaQzokUHlalWm1"
		address = 'apiAddress'
		profile = 'defualt'
		CLI().auth(key,address,profile)
		home = os.environ['HOME']
		keyfile = open(home+"/.algorithmia_api_key","r")
		result = keyfile.read()
		keyfile.close()
		self.assertEqual(result, key)


if __name__ == '__main__':
    unittest.main()