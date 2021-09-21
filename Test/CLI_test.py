import sys
# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest
import os
import json
import Algorithmia
from Algorithmia.CLI import CLI
import argparse
import shutil

class CLITest(unittest.TestCase):
	def setUp(self):
		# create a directory to use in testing the cp command 
		self.client = Algorithmia.client()
		CLI().mkdir("data://.my/moredata", self.client)
		if(not os.path.exists("./TestFiles/")):
			os.mkdir("./TestFiles/")
	
	def test_ls(self):
		parentDir = "data://.my/"
		newDir = "test"

		CLI().mkdir(parentDir+newDir, self.client)
		result = CLI().ls(parentDir, self.client)
		self.assertTrue(result is not None and "moredata" in result and newDir in result)
		
		CLI().rmdir(parentDir+newDir, self.client)


	def test_mkdir(self):

		parentDir = "data://.my/"
		newDir = "test"

		CLI().mkdir(parentDir+newDir, self.client)
		result = CLI().ls(parentDir, self.client)
		self.assertTrue(newDir in result)
		
		CLI().rmdir(parentDir+newDir, self.client)

	def test_rmdir(self):
		parentDir = "data://.my/"
		newDir = "testRmdir"

		CLI().mkdir(parentDir+newDir, self.client)
		result = CLI().ls(parentDir, self.client)
		self.assertTrue(newDir in result)
		
		CLI().rmdir(parentDir+newDir, self.client)

		result = CLI().ls(parentDir, self.client)
		self.assertTrue(newDir not in result)

	def test_cat(self):
		file = "data://.my/moredata/test.txt"
		localfile = "./TestFiles/test.txt"
		fileContents = "some text in test file"

		CLI().rm(file, self.client)
		testfile = open(localfile, "w")
		testfile.write(fileContents)
		testfile.close()

		CLI().cp([localfile],file,self.client)

		result = CLI().cat([file],self.client)
		self.assertEqual(result, fileContents)

	def test_get_build_logs(self):
		user=os.environ.get('ALGO_USER_NAME')
		algo="Echo"
		
		result = json.loads(CLI().getBuildLogs(user,algo,self.client))
		if "error" in result:
			print(result)
		self.assertTrue("error" not in result)


#local to remote
	def test_cp_L2R(self):
		localfile = "./TestFiles/test.txt"
		testfile = open(localfile, "w")
		testfile.write("some text")
		testfile.close()

		src = [localfile]
		dest = "data://.my/moredata/test.txt"
		CLI().cp(src,dest,self.client)

		result = CLI().ls("data://.my/moredata/",self.client)
		self.assertTrue("test.txt" in result)

#remote to remote
	def test_cp_R2R(self):

		src = ["data://.my/moredata/test.txt"]
		dest = "data://.my/moredata/test2.txt"
		CLI().cp(src,dest,self.client)

		result = CLI().ls("data://.my/moredata/",self.client)
		self.assertTrue("test2.txt" in result)

#remote to local
	def test_cp_R2L(self):
		src = ["data://.my/moredata/test.txt"]
		dest = "./test.txt"

		CLI().cp(src,dest,self.client)
		self.assertTrue(os.path.isfile(dest))

	def test_run(self):
		name = "util/Echo"
		inputs = "test"

		parser = argparse.ArgumentParser('CLI for interacting with Algorithmia')

		subparsers = parser.add_subparsers(help = 'sub cmd',dest = 'subparser_name')
		parser_run = subparsers.add_parser('run', help = 'algo run <algo> [input options] <args..> [output options]')
		
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
		
		args = parser.parse_args(['run',name,'-d',inputs])

		result = CLI().runalgo(args, self.client)
		self.assertEqual(result, inputs)
	
	def test_auth(self):
		#key for test account
		key = os.getenv('ALGORITHMIA_API_KEY')
		address = 'apiAddress'
		profile = 'default'
		CLI().auth(key,address,profile=profile)
		resultK = CLI().getAPIkey(profile)
		resultA = CLI().getAPIaddress(profile)
		self.assertEqual(resultK, key)
		self.assertEqual(resultA, address)

	def test_auth_cert(self):

		localfile = "./TestFiles/fakecert.pem"

		testfile = open(localfile, "w")
		testfile.write("")
		testfile.close()

		#key for test account
		key = os.getenv('ALGORITHMIA_API_KEY')
		address = 'apiAddress'
		cacert = localfile
		profile = 'test'

		CLI().auth(key,address,cacert,profile)
		resultK = CLI().getAPIkey(profile)
		resultA = CLI().getAPIaddress(profile)
		resultC = CLI().getCert(profile)
		self.assertEqual(resultK, key)
		self.assertEqual(resultA, address)
		self.assertEqual(resultC, cacert)
	
	def test_get_environment(self):
		result = CLI().get_environment_by_language("python2",self.client)
		print(result)
		if("error" in result):
			print(result)
		self.assertTrue(result is not None and "Python 2.7" in result)

	def test_list_languages(self):
		result = CLI().list_languages(self.client)
		if("error" in result[0]):
			print(result)
		self.assertTrue(result is not None and "anaconda3" in result[1])


	def test_rm(self):
		localfile = "./TestFiles/testRM.txt"

		testfile = open(localfile, "w")
		testfile.write("some text")
		testfile.close()

		src = [localfile]
		dest = "data://.my/moredata/"
		CLI().cp(src,dest,self.client)
		
		result1 = CLI().ls(dest,self.client)
		
		CLI().rm("data://.my/moredata/testRM.txt",self.client)
		
		result2 = CLI().ls(dest,self.client)

		self.assertTrue("testRM.txt" in result1 and "testRM.txt" not in result2)

	def test_get_template(self):
		filename = "./temptest"
		envid = "36fd467e-fbfe-4ea6-aa66-df3f403b7132"
		response = CLI().get_template(envid,filename,self.client)
		print(response)
		self.assertTrue(response.ok)
		try:
			shutil.rmtree(filename)
		except OSError as e:
			print(e)
		


if __name__ == '__main__':
    unittest.main()