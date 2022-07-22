import sys
import os
from Algorithmia.errors import AlgorithmException
from Algorithmia.algorithm import OutputType
import Algorithmia

# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest

if sys.version_info.major >= 3:

    class AlgoDummyTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.client = Algorithmia.client(api_address="http://localhost:8080", api_key="simabcd123")
            cls.environment_id = "abcd-123"

        def test_call_customCert(self):
            result = self.client.algo('quality/echo').pipe(bytearray('foo', 'utf-8'))
            self.assertEqual('binary', result.metadata.content_type)
            self.assertEqual(bytearray('foo', 'utf-8'), result.result)



        def test_normal_call(self):
            result = self.client.algo('quality/echo').pipe("foo")
            self.assertEqual("text", result.metadata.content_type)
            self.assertEqual("foo", result.result)

        def test_async_call(self):
            result = self.client.algo('quality/echo').set_options(output=OutputType.void).pipe("foo")
            self.assertTrue(hasattr(result, "async_protocol"))
            self.assertTrue(hasattr(result, "request_id"))

        def test_raw_call(self):
            result = self.client.algo('quality/echo').set_options(output=OutputType.raw).pipe("foo")
            self.assertEqual("foo", result)

        def test_dict_call(self):
            result = self.client.algo('quality/echo').pipe({"foo": "bar"})
            self.assertEqual("json", result.metadata.content_type)
            self.assertEqual({"foo": "bar"}, result.result)

        def test_algo_exists(self):
            result = self.client.algo('quality/echo').exists()
            self.assertEqual(True, result)

        def test_algo_no_exists(self):
            result = self.client.algo('quality/not_echo').exists()
            self.assertEqual(False, result)

        #TODO: add more coverage examples to check kwargs
        def test_get_versions(self):
            result = self.client.algo('quality/echo').versions()
            self.assertTrue('results' in result)
            self.assertTrue('version_info' in result['results'][0])
            self.assertTrue('semantic_version' in result['results'][0]['version_info'])
            self.assertEqual('0.1.0', result['results'][0]['version_info']['semantic_version'])

        def test_text_unicode(self):
            telephone = u"\u260E"
            # Unicode input to pipe()
            result1 = self.client.algo('quality/echo').pipe(telephone)
            self.assertEqual('text', result1.metadata.content_type)
            self.assertEqual(telephone, result1.result)

            # Unicode return in .result
            result2 = self.client.algo('quality/echo').pipe(result1.result)
            self.assertEqual('text', result2.metadata.content_type)
            self.assertEqual(telephone, result2.result)
            
        def test_algo_info(self):
            result = self.client.algo('quality/echo').info()
            self.assertTrue('results' in result)
            self.assertTrue('resource_type' in result['results'][0])
            self.assertTrue(result['results'][0]['resource_type'] == "algorithm")

        def test_update_algo(self):
            details = {
                "summary": "Example Summary",
                "label": "QA",
                "tagline": "Example Tagline"
            }
            settings = {
                "source_visibility": "open",
                "algorithm_environment": self.environment_id,
                "license": "apl",
                "network_access": "isolated",
                "pipeline_enabled": False
            }
            version_info = {
                "sample_input": "hello"
            }
            result = self.client.algo('quality/echo').update(details=details, settings=settings, version_info=version_info)
            self.assertTrue('id' in result)


        def test_get_build_by_id(self):
            result = self.client.algo("quality/echo").get_build("1a392e2c-b09f-4bae-a616-56c0830ac8e5")
            self.assertTrue('commit_sha' in result)

        def test_get_build_logs(self):
            result = self.client.algo("quality/echo").get_build_logs("1a392e2c-b09f-4bae-a616-56c0830ac8e5")
            self.assertTrue('logs' in result)

        def test_get_scm_status(self):
            result = self.client.algo("quality/echo").get_scm_status()
            self.assertTrue('scm_connection_status' in result)

        def test_exception_ipa_algo(self):
            try:
                result = self.client.algo('zeryx/raise_exception').pipe("")
            except AlgorithmException as e:
                self.assertEqual(e.message, "This is an exception")

        def test_algorithm_programmatic_create_process(self):
            algorithm_name = "hello"
            payload = "John"
            expected_response = "hello John"
            full_path = "quality/" + algorithm_name
            details = {
                "summary": "Example Summary",
                "label": "QA",
                "tagline": "Example Tagline"
            }
            settings = {
                "source_visibility": "open",
                "algorithm_environment": self.environment_id,
                "license": "apl",
                "network_access": "isolated",
                "pipeline_enabled": False
            }
            version_info = {
                "sample_input": "hello"
            }
            created_algo = self.client.algo(full_path)
            print("about to create algo")
            response = created_algo.create(details=details, settings=settings, version_info=version_info)
            print("created algo")
            self.assertEqual(response['name'], algorithm_name, "algorithm creation failed")

            # --- Creation complete, compiling

            response = created_algo.compile()
            git_hash = response['version_info']['git_hash']
            algo_with_build = self.client.algo(full_path + "/" + git_hash)
            self.assertEqual(response['name'], created_algo.algoname)

            # --- compiling complete, now testing algorithm request
            response = algo_with_build.pipe(payload).result
            self.assertEqual(response, expected_response, "compiling failed")

            # --- testing complete, now publishing new release.

            pub_settings = {"algorithm_callability": "private"}
            pub_version_info = {
                "release_notes": "created programmatically",
                "sample_input": payload,
                "version_type": "minor"
            }
            pub_details = {"label": "testing123"}

            response = algo_with_build.publish(
                details=pub_details,
                settings=pub_settings,
                version_info=pub_version_info
            )
            self.assertEqual(response["version_info"]["semantic_version"], "0.1.0",
                             "Publishing failed, semantic version is not correct.")

            # --- publishing complete, getting additional information

            response = created_algo.info(git_hash)

            self.assertEqual(response['version_info']['semantic_version'], "0.1.0", "information is incorrect")


        def test_set_secret(self):
            short_name = "tst"
            secret_key = "test_key"
            secret_value = "test_value"
            description = "loreum epsum"
            response = self.client.algo("quality/echo").set_secret(short_name, secret_key, secret_value, description)
            self.assertEqual(response['id'], "959af771-7cd8-4981-91c4-70def15bbcdc", "invalid ID for created secret")


else:
    class AlgoTest(unittest.TestCase):
        def setUp(self):
            self.client = Algorithmia.client()

        def test_call_customCert(self):
            open("./test.pem", 'w')
            c = Algorithmia.client(ca_cert="./test.pem")
            result = c.algo('quality/echo').pipe(bytearray('foo', 'utf-8'))
            self.assertEqual('binary', result.metadata.content_type)
            self.assertEqual(bytearray('foo', 'utf-8'), result.result)
            try:
                os.remove("./test.pem")
            except OSError as e:
                print(e)

        def test_call_binary(self):
            result = self.client.algo('quality/echo').pipe(bytearray('foo', 'utf-8'))
            self.assertEqual('binary', result.metadata.content_type)
            self.assertEqual(bytearray('foo', 'utf-8'), result.result)

        def test_async_call(self):
            result = self.client.algo('quality/echo').set_options(output=OutputType.void).pipe("foo")
            self.assertTrue(hasattr(result, "async_protocol"))
            self.assertTrue(hasattr(result, "request_id"))

        def test_raw_call(self):
            result = self.client.algo('quality/echo').set_options(output=OutputType.raw).pipe("foo")
            self.assertEqual("foo", result)

        #TODO: add more coverage examples to check kwargs
        def test_get_versions(self):
            result = self.client.algo('quality/echo').versions()
            self.assertTrue('results' in result)
            self.assertTrue('version_info' in result['results'][0])
            self.assertTrue('semantic_version' in result['results'][0]['version_info'])
            self.assertEqual('0.1.0', result['results'][0]['version_info']['semantic_version'])

        def test_text_unicode(self):
            telephone = u"\u260E"

            # Unicode input to pipe()
            result1 = self.client.algo('quality/echo').pipe(telephone)
            self.assertEqual('text', result1.metadata.content_type)
            self.assertEqual(telephone, result1.result)

            # Unicode return in .result
            result2 = self.client.algo('quality/echo').pipe(result1.result)
            self.assertEqual('text', result2.metadata.content_type)
            self.assertEqual(telephone, result2.result)


        def test_get_scm_status(self):
            result = self.client.algo("quality/echo").get_scm_status()
            self.assertTrue('scm_connection_status' in result)

        def test_exception_ipa_algo(self):
            try:
                result = self.client.algo('zeryx/raise_exception').pipe("")
            except AlgorithmException as e:
                self.assertEqual(e.message, "This is an exception")

if __name__ == '__main__':
    unittest.main()
