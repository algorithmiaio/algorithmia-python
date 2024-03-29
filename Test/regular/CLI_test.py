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

if sys.version_info.major >= 3:
    class CLIDummyTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.client = Algorithmia.client(api_address="http://localhost:8080", api_key="simabcd123")
            cls.bearerClient = Algorithmia.client(api_address="http://localhost:8080", bearer_token="simabcd123.token.token")

        def test_run(self):
            name = "util/Echo"
            inputs = "test"

            parser = argparse.ArgumentParser('CLI for interacting with Algorithmia')

            subparsers = parser.add_subparsers(help='sub cmd', dest='subparser_name')
            parser_run = subparsers.add_parser('run', help='algo run <algo> [input options] <args..> [output options]')

            parser_run.add_argument('algo')
            parser_run.add_argument('-d', '--data', action='store', help='detect input type', default=None)
            parser_run.add_argument('-t', '--text', action='store', help='treat input as text', default=None)
            parser_run.add_argument('-j', '--json', action='store', help='treat input as json data', default=None)
            parser_run.add_argument('-b', '--binary', action='store', help='treat input as binary data', default=None)
            parser_run.add_argument('-D', '--data-file', action='store', help='specify a path to an input file',
                                    default=None)
            parser_run.add_argument('-T', '--text-file', action='store', help='specify a path to a text file',
                                    default=None)
            parser_run.add_argument('-J', '--json-file', action='store', help='specify a path to a json file',
                                    default=None)
            parser_run.add_argument('-B', '--binary-file', action='store', help='specify a path to a binary file',
                                    default=None)
            parser_run.add_argument('--timeout', action='store', type=int, default=300,
                                    help='specify a timeout (seconds)')
            parser_run.add_argument('--debug', action='store_true',
                                    help='print the stdout from the algo <this only works for the owner>')
            parser_run.add_argument('--profile', action='store', type=str, default='default')
            parser_run.add_argument('-o', '--output', action='store', default=None, type=str)

            args = parser.parse_args(['run', name, '-d', inputs])

            result = CLI().runalgo(args, self.client)
            self.assertEqual(result, inputs)

        def test_run_token(self):
            name = "util/Echo"
            inputs = "test"

            parser = argparse.ArgumentParser('CLI for interacting with Algorithmia')

            subparsers = parser.add_subparsers(help='sub cmd', dest='subparser_name')
            parser_run = subparsers.add_parser('run', help='algo run <algo> [input options] <args..> [output options]')

            parser_run.add_argument('algo')
            parser_run.add_argument('-d', '--data', action='store', help='detect input type', default=None)
            parser_run.add_argument('-t', '--text', action='store', help='treat input as text', default=None)
            parser_run.add_argument('-j', '--json', action='store', help='treat input as json data', default=None)
            parser_run.add_argument('-b', '--binary', action='store', help='treat input as binary data', default=None)
            parser_run.add_argument('-D', '--data-file', action='store', help='specify a path to an input file',
                                    default=None)
            parser_run.add_argument('-T', '--text-file', action='store', help='specify a path to a text file',
                                    default=None)
            parser_run.add_argument('-J', '--json-file', action='store', help='specify a path to a json file',
                                    default=None)
            parser_run.add_argument('-B', '--binary-file', action='store', help='specify a path to a binary file',
                                    default=None)
            parser_run.add_argument('--timeout', action='store', type=int, default=300,
                                    help='specify a timeout (seconds)')
            parser_run.add_argument('--debug', action='store_true',
                                    help='print the stdout from the algo <this only works for the owner>')
            parser_run.add_argument('--profile', action='store', type=str, default='default')
            parser_run.add_argument('-o', '--output', action='store', default=None, type=str)

            args = parser.parse_args(['run', name, '-d', inputs])

            result = CLI().runalgo(args, self.bearerClient)
            self.assertEqual(result, inputs)


class CLIMainTest(unittest.TestCase):
    def setUp(self):
        # create a directory to use in testing the cp command
        self.client = Algorithmia.client()
        CLI().mkdir("data://.my/moredata", self.client)
        if not os.path.exists("../TestFiles/"):
            os.mkdir("../TestFiles/")

    def test_ls(self):
        parentDir = "data://.my/"
        newDir = "test"

        CLI().mkdir(parentDir + newDir, self.client)
        result = CLI().ls(parentDir, self.client)
        self.assertTrue(result is not None and "moredata" in result and newDir in result)

        CLI().rmdir(parentDir + newDir, self.client)

    def test_mkdir(self):

        parentDir = "data://.my/"
        newDir = "test"

        CLI().mkdir(parentDir + newDir, self.client)
        result = CLI().ls(parentDir, self.client)
        self.assertTrue(newDir in result)

        CLI().rmdir(parentDir + newDir, self.client)

    def test_rmdir(self):
        parentDir = "data://.my/"
        newDir = "testRmdir"

        CLI().mkdir(parentDir + newDir, self.client)
        result = CLI().ls(parentDir, self.client)
        self.assertTrue(newDir in result)

        CLI().rmdir(parentDir + newDir, self.client)

        result = CLI().ls(parentDir, self.client)
        self.assertTrue(newDir not in result)

    def test_cat(self):
        file = "data://.my/moredata/test.txt"
        localfile = "./../TestFiles/test.txt"
        fileContents = "some text in test file"

        CLI().rm(file, self.client)
        testfile = open(localfile, "w")
        testfile.write(fileContents)
        testfile.close()

        CLI().cp([localfile], file, self.client)

        result = CLI().cat([file], self.client)
        self.assertEqual(result, fileContents)

    def test_get_build_logs(self):
        user = os.environ.get('ALGO_USER_NAME')
        algo = "Echo"

        result = json.loads(CLI().getBuildLogs(user, algo, self.client))
        if "error" in result:
            print(result)
        self.assertTrue("error" not in result)

    # local to remote
    def test_cp_L2R(self):
        localfile = "./../TestFiles/test.txt"
        testfile = open(localfile, "w")
        testfile.write("some text")
        testfile.close()

        src = [localfile]
        dest = "data://.my/moredata/test.txt"
        CLI().cp(src, dest, self.client)

        result = CLI().ls("data://.my/moredata/", self.client)
        self.assertTrue("test.txt" in result)

    # remote to remote
    def test_cp_R2R(self):

        src = ["data://.my/moredata/test.txt"]
        dest = "data://.my/moredata/test2.txt"
        CLI().cp(src, dest, self.client)

        result = CLI().ls("data://.my/moredata/", self.client)
        self.assertTrue("test2.txt" in result)

    # remote to local
    def test_cp_R2L(self):
        src = ["data://.my/moredata/test.txt"]
        dest = "./../test.txt"

        CLI().cp(src, dest, self.client)
        self.assertTrue(os.path.isfile(dest))

    def test_auth(self):
        # key for test account
        key = os.getenv('ALGORITHMIA_API_KEY')
        api_address = "https://api.algorithmia.com"
        profile = 'default'
        CLI().auth(api_address, key, profile=profile)
        resultK = CLI().getAPIkey(profile)
        resultA = CLI().getAPIaddress(profile)
        self.assertEqual(resultK, key)
        self.assertEqual(resultA, api_address)

    def test_auth_cert(self):

        localfile = "./../TestFiles/fakecert.pem"

        testfile = open(localfile, "w")
        testfile.write("")
        testfile.close()

        # key for test account
        key = os.getenv('ALGORITHMIA_API_KEY')
        address = 'https://api.algorithmia.com'
        cacert = localfile
        profile = 'test'

        CLI().auth(address, key, cacert=cacert, profile=profile)
        resultK = CLI().getAPIkey(profile)
        resultA = CLI().getAPIaddress(profile)
        resultC = CLI().getCert(profile)
        self.assertEqual(resultK, key)
        self.assertEqual(resultA, address)
        self.assertEqual(resultC, cacert)
    
    def test_auth_token(self):
        address = 'https://api.algorithmia.com'
        bearer = 'testtokenabcd'
        profile = 'test'

        CLI().auth(apiaddress=address, bearer=bearer, profile=profile)
        resultA = CLI().getAPIaddress(profile)
        resultT = CLI().getBearerToken(profile)
        self.assertEqual(resultA, address)
        self.assertEqual(resultT, bearer)

    def test_get_environment(self):
        result = CLI().get_environment_by_language("python2", self.client)
        print(result)
        if ("error" in result):
            print(result)
        self.assertTrue(result is not None and "display_name" in result)

    def test_list_languages(self):
        result = CLI().list_languages(self.client)
        if ("error" in result[0]):
            print(result)
        self.assertTrue(result is not None and "anaconda3" in result[1])

    def test_rm(self):
        localfile = "./../TestFiles/testRM.txt"

        testfile = open(localfile, "w")
        testfile.write("some text")
        testfile.close()

        src = [localfile]
        dest = "data://.my/moredata/"
        CLI().cp(src, dest, self.client)

        result1 = CLI().ls(dest, self.client)

        CLI().rm("data://.my/moredata/testRM.txt", self.client)

        result2 = CLI().ls(dest, self.client)

        self.assertTrue("testRM.txt" in result1 and "testRM.txt" not in result2)

    def test_get_template(self):
        filename = "./../temptest"
        envid = "36fd467e-fbfe-4ea6-aa66-df3f403b7132"
        response = CLI().get_template(envid, filename, self.client)
        print(response)
        self.assertTrue(response.ok)
        try:
            shutil.rmtree(filename)
        except OSError as e:
            print(e)

    def test_api_address_auth(self):
        api_key = os.getenv('ALGORITHMIA_API_KEY')
        api_address = "https://api.algorithmia.com"
        CLI().auth(api_address, api_key)
        profile = "default"

        client = Algorithmia.client(CLI().getAPIkey(profile), CLI().getAPIaddress(profile), CLI().getCert(profile))
        result2 = CLI().ls("data://.my", client)
        print(result2)
        self.assertTrue(result2 != "")


if __name__ == '__main__':
    unittest.main()
