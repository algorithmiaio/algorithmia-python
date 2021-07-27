import os
import shutil
import sys
from datetime import datetime
from random import random
from random import seed

sys.path = ['../'] + sys.path

import unittest
import Algorithmia

if sys.version_info.major == 3:
    unicode = str

class ClientTest(unittest.TestCase):
    seed(datetime.now().microsecond)

    username = "a_Mrtest"
    org_name = "a_myOrg"

    def setUp(self):
        self.admin_api_key = unicode(os.environ.get('ALGORITHMIA_A_KEY'))

        self.username = self.username + str(int(random() * 10000))
        self.org_name = self.org_name + str(int(random() * 10000))
        self.c = Algorithmia.client(api_address="https://test.algorithmia.com",
                                    api_key=self.admin_api_key)

    def test_create_user(self):
        response = self.c.create_user(
            {"username": self.username, "email": self.username + "@algo.com", "passwordHash": "",
             "shouldCreateHello": False})
        self.assertEqual(self.username, response['username'])

    def test_get_org_types(self):
        response = self.c.get_org_types()
        self.assertTrue(len(response) > 0)

    def test_create_org(self):
        response = self.c.create_org(
            {"org_name": self.org_name, "org_label": "some label", "org_contact_name": "Some owner",
             "org_email": self.org_name + "@algo.com", "type_id": "basic"})

        self.assertEqual(self.org_name, response[u'org_name'])

    def test_get_org(self):
        response = self.c.get_org("a_myOrg84")
        self.assertEqual("a_myOrg84", response['org_name'])

    def test_get_environment(self):
        client = Algorithmia.client(api_key=unicode(os.environ.get('ALGORITHMIA_API_KEY')))
        response = client.get_environment("python2")

        if u'error' not in response:
            self.assertTrue(response is not None and u'environments' in response)

    def test_get_build_logs(self):
        client = Algorithmia.client(api_address='https://test.algorithmia.com',
                                    api_key=unicode(os.environ.get('ALGORITHMIA_A_KEY')))
        user = unicode(os.environ.get('ALGO_USER_NAME'))
        algo = unicode('echo')
        algo_path = u'%s/%s' % (user, algo)
        result = client.algo(algo_path).build_logs()

        if u'error' in result:
            print(result)

        self.assertTrue(u'error' not in result)

    def test_get_build_logs_no_ssl(self):
        client = Algorithmia.client(api_address='https://test.algorithmia.com',
                                    api_key=unicode(os.environ.get('ALGORITHMIA_A_KEY')), ca_cert=False)
        user = unicode(os.environ.get('ALGO_USER_NAME'))
        algo = u'Echo'
        result = client.algo(user + '/' + algo).build_logs()
        if u'error' in result:
            print(result)
        self.assertTrue("error" not in result)

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

        response = self.c.edit_org(org_name, obj)
        if type(response) is dict:
            print(response)
        else:
            self.assertEqual(204, response.status_code)

    def test_get_template(self):
        filename = "./temptest"
        response = self.c.get_template("36fd467e-fbfe-4ea6-aa66-df3f403b7132", filename)

        if type(response) is dict:
            self.assertTrue(u'error' in response or u'message' in response)
        else:
            self.assertTrue(response.ok)
            try:
                shutil.rmtree(filename)
            except OSError as e:
                print(e)

    def test_get_supported_languages(self):
        response = self.c.get_supported_languages()
        self.assertTrue(response is not None)

        if type(response) is not list:
            self.assertTrue(u'error' in response)
        else:
            language_found = any('anaconda3' in languages['name'] for languages in response)
            self.assertTrue(response is not None and language_found)

    def test_invite_to_org(self):
        response = self.c.invite_to_org("a_myOrg38", "a_Mrtest4")
        if type(response) is dict:
            self.assertTrue(u'error' in response)
        else:
            self.assertEqual(200, response.status_code)

    # This test will require updating after the /v1/organizations/{org_name}/errors endpoint has been
    # deployed to the remote environment.
    def test_get_organization_errors(self):
        response = self.c.get_organization_errors(self.org_name)
        self.assertTrue(response is not None)

        if type(response) is list:
            self.assertEqual(0, len(response), 'Received unexpected result, should have been 0.')

    def test_get_user_errors(self):
        response = self.c.get_user_errors(self.username)

        self.assertTrue(response is not None)
        self.assertEqual(0, len(response))

    def test_get_algorithm_errors(self):
        response = self.c.get_algorithm_errors('hello')
        self.assertTrue(response is not None)

        if type(response) is dict:
            self.assertTrue(u'error' in response)
        else:
            self.assertEqual(404, response.status_code)


if __name__ == '__main__':
    unittest.main()
