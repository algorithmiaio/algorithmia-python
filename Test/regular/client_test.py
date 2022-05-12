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
            try:
                _ = self.client.get_algorithm_errors('hello')
                self.assertFalse(True)
            except AlgorithmException as e:
                self.assertTrue(e.message == "No such algorithm")


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
if __name__ == '__main__':
    unittest.main()
