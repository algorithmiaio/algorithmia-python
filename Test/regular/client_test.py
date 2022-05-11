import os
import shutil
import sys
from datetime import datetime
from random import random
from random import seed

sys.path = ['../'] + sys.path

import unittest
import Algorithmia
from Algorithmia.errors import AlgorithmException
from uuid import uuid4

if sys.version_info.major >= 3:
    unicode = str


    class ClientDummyTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.client = Algorithmia.client(api_address="http://localhost:8080", api_key="simabcd123")
        admin_username = "a_Mrtest"
        admin_org_name = "a_myOrg"
        environment_name = "Python 3.9"

        def setUp(self):
            self.admin_username = self.admin_username + str(int(random() * 10000))
            self.admin_org_name = self.admin_org_name + str(int(random() * 10000))

            self.environment_id = "abcd-123"

        def test_create_user(self):
            response = self.client.create_user(
                {"username": self.admin_username, "email": self.admin_username + "@algo.com", "passwordHash": "",
                 "shouldCreateHello": False})

            if type(response) is dict:
                self.assertEqual(self.admin_username, response['username'])
            else:
                self.assertIsNotNone(response)

        def test_get_org_types(self):
            response = self.client.get_org_types()
            self.assertTrue(len(response) > 0)

        def test_create_org(self):
            response = self.client.create_org(
                {"org_name": self.admin_org_name, "org_label": "some label", "org_contact_name": "Some owner",
                 "org_email": self.admin_org_name + "@algo.com", "type_id": "basic"})

            self.assertEqual(self.admin_org_name, response[u'org_name'])

        def test_get_org(self):
            response = self.client.get_org("a_myOrg84")
            self.assertEqual("a_myOrg84", response['org_name'])

        def test_get_environment(self):
            response = self.client.get_environment("python2")

            if u'error' not in response:
                self.assertTrue(response is not None and u'environments' in response)

        def test_edit_org(self):
            org_name = "a_myOrg84"

            obj = {
                "id": "b85d8c4e-7f3c-40b9-9659-6adc2cb0e16f",
                "org_name": "a_myOrg84",
                "org_label": "some label",
                "org_contact_name": "Some owner",
                "org_email": "a_myOrg84@algo.com",
                "org_created_at": "2020-11-30T23:51:40",
                "org_url": "https://algorithmia.com",
                "type_id": "basic",
                "resource_type": "organization"
            }

            response = self.client.edit_org(org_name, obj)
            if type(response) is dict:
                print(response)
            else:
                self.assertEqual(204, response.status_code)

        def test_get_supported_languages(self):
            response = self.client.get_supported_languages()
            self.assertTrue(response is not None)

            if type(response) is not list:
                self.assertTrue(u'error' in response)
            else:
                language_found = any('anaconda3' in languages['name'] for languages in response)
                self.assertTrue(response is not None and language_found)

        def test_invite_to_org(self):
            response = self.client.invite_to_org("a_myOrg38", "a_Mrtest4")
            if type(response) is dict:
                self.assertTrue(u'error' in response)
            else:
                self.assertEqual(200, response.status_code)

        # This test will require updating after the /v1/organizations/{org_name}/errors endpoint has been
        # deployed to the remote environment.
        def test_get_organization_errors(self):
            response = self.client.get_organization_errors(self.admin_org_name)
            self.assertTrue(response is not None)

            if type(response) is list:
                self.assertEqual(0, len(response), 'Received unexpected result, should have been 0.')

        def test_get_user_errors(self):
            response = self.client.get_user_errors(self.admin_username)

            self.assertTrue(response is not None)
            self.assertEqual(0, len(response))

        def test_get_algorithm_errors(self):
            response = self.client.get_algorithm_errors('hello')
            self.assertTrue(response is not None)

            if type(response) is dict:
                self.assertTrue(u'error' in response)
            else:
                self.assertEqual(404, response.status_code)

        def test_algorithm_programmatic_create_process(self):
            algorithm_name = "algo_e2d_test"
            payload = "John"
            expected_response = "hello John"
            full_path = "a_Mrtest/" + algorithm_name
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

        def test_no_auth_client(self):

            key = os.environ.get('ALGORITHMIA_API_KEY', "")
            if key != "":
                del os.environ['ALGORITHMIA_API_KEY']

            client = Algorithmia.client(api_address="http://localhost:8080")
            error = None
            try:
                client.algo("demo/hello").pipe("world")
            except Exception as e:
                error = e
            finally:
                os.environ['ALGORITHMIA_API_KEY'] = key
                self.assertEqual(str(error), str(AlgorithmException(message="authorization required", stack_trace=None, error_type=None)))

else:
    class ClientTest(unittest.TestCase):
        seed(datetime.now().microsecond)
        # due to legacy reasons, regular client tests are tested against api.algorithmia.com, whereas admin api tests
        # are run against test.algorithmia.com.
        admin_username = "a_Mrtest"
        admin_org_name = "a_myOrg"
        environment_name = "Python 3.9"

        def setUp(self):
            self.admin_api_key = unicode(os.environ.get('ALGORITHMIA_A_KEY'))
            self.regular_api_key = unicode(os.environ.get('ALGORITHMIA_API_KEY'))

            self.admin_username = self.admin_username + str(int(random() * 10000))
            self.admin_org_name = self.admin_org_name + str(int(random() * 10000))
            self.admin_client = Algorithmia.client(api_address="https://api.algorithmia.com",
                                                   api_key=self.admin_api_key)
            self.regular_client = Algorithmia.client(api_address='https://api.algorithmia.com',
                                                     api_key=self.regular_api_key)

            environments = self.regular_client.get_environment("python3")
            for environment in environments['environments']:
                if environment['display_name'] == self.environment_name:
                    self.environment_id = environment['id']

        def test_create_user(self):
            response = self.admin_client.create_user(
                {"username": self.admin_username, "email": self.admin_username + "@algo.com", "passwordHash": "",
                 "shouldCreateHello": False})

            if type(response) is dict:
                self.assertEqual(self.admin_username, response['username'])
            else:
                self.assertIsNotNone(response)

        def test_get_org_types(self):
            response = self.admin_client.get_org_types()
            self.assertTrue(len(response) > 0)

        def test_create_org(self):
            response = self.admin_client.create_org(
                {"org_name": self.admin_org_name, "org_label": "some label", "org_contact_name": "Some owner",
                 "org_email": self.admin_org_name + "@algo.com", "type_id": "basic"})

            self.assertEqual(self.admin_org_name, response[u'org_name'])

        def test_get_org(self):
            response = self.admin_client.get_org("a_myOrg84")
            self.assertEqual("a_myOrg84", response['org_name'])

        def test_get_environment(self):
            response = self.admin_client.get_environment("python2")

            if u'error' not in response:
                self.assertTrue(response is not None and u'environments' in response)

        def test_edit_org(self):
            org_name = "a_myOrg84"

            obj = {
                "id": "b85d8c4e-7f3c-40b9-9659-6adc2cb0e16f",
                "org_name": "a_myOrg84",
                "org_label": "some label",
                "org_contact_name": "Some owner",
                "org_email": "a_myOrg84@algo.com",
                "org_created_at": "2020-11-30T23:51:40",
                "org_url": "https://algorithmia.com",
                "type_id": "basic",
                "resource_type": "organization"
            }

            response = self.admin_client.edit_org(org_name, obj)
            if type(response) is dict:
                print(response)
            else:
                self.assertEqual(204, response.status_code)

        def test_get_template(self):
            filename = "./temptest"
            response = self.admin_client.get_template("36fd467e-fbfe-4ea6-aa66-df3f403b7132", filename)

            if type(response) is dict:
                self.assertTrue(u'error' in response or u'message' in response)
            else:
                self.assertTrue(response.ok)
                try:
                    shutil.rmtree(filename)
                except OSError as e:
                    print(e)

        def test_get_supported_languages(self):
            response = self.admin_client.get_supported_languages()
            self.assertTrue(response is not None)

            if type(response) is not list:
                self.assertTrue(u'error' in response)
            else:
                language_found = any('anaconda3' in languages['name'] for languages in response)
                self.assertTrue(response is not None and language_found)

        def test_invite_to_org(self):
            response = self.admin_client.invite_to_org("a_myOrg38", "a_Mrtest4")
            if type(response) is dict:
                self.assertTrue(u'error' in response)
            else:
                self.assertEqual(200, response.status_code)

        # This test will require updating after the /v1/organizations/{org_name}/errors endpoint has been
        # deployed to the remote environment.
        def test_get_organization_errors(self):
            response = self.admin_client.get_organization_errors(self.admin_org_name)
            self.assertTrue(response is not None)

            if type(response) is list:
                self.assertEqual(0, len(response), 'Received unexpected result, should have been 0.')

        def test_get_user_errors(self):
            response = self.admin_client.get_user_errors(self.admin_username)

            self.assertTrue(response is not None)
            self.assertEqual(0, len(response))

        def test_get_algorithm_errors(self):
            response = self.admin_client.get_algorithm_errors('hello')
            self.assertTrue(response is not None)

            if type(response) is dict:
                self.assertTrue(u'error' in response)
            else:
                self.assertEqual(404, response.status_code)

        def test_algo_freeze(self):
            self.regular_client.freeze("Test/resources/manifests/example_manifest.json", "Test/resources/manifests")

if __name__ == '__main__':
    unittest.main()
