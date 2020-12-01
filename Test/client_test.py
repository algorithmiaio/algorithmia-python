from datetime import datetime, time
import sys
import os
from random import seed
from random import random
# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest

import Algorithmia

class client_test(unittest.TestCase):
    seed(datetime.now().microsecond)

    username = "a_Mrtest"
    orgname = "a_myOrg"
    
    def setUp(self):
        self.username = self.username + str(int(random()*10000))
        self.orgname = self.orgname + str(int(random()*10000))
        self.c = Algorithmia.client(api_address="https://test.algorithmia.com",api_key=os.environ.get('ALGORITHMIA_A_KEY'))

    def test_create_user(self):
        response = self.c.create_user({"username":self.username, "email": self.username+"@algo.com", "passwordHash":"", "shouldCreateHello": False})
        self.assertEqual(self.username,response['username']) 

    def test_create_org(self):
        response = self.c.create_org({"org_name": self.orgname, "org_label": "some label", "org_contact_name": "Some owner", "org_email": self.orgname+"@algo.com"})
        self.assertEqual(self.orgname,response['org_name'])

    def test_invite_to_org(self):
        response = self.c.invite_to_org("a_myOrg38","a_Mrtest4")
        self.assertEqual(200,response.status_code)


if __name__ == '__main__':
    unittest.main()