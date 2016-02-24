import sys
sys.path.append("../")

import unittest

from Algorithmia.acl_type import AclType

class AclTypeTest(unittest.TestCase):
    def test_types(self):
        self.assertTrue(AclType.private.acl_string is None)
        self.assertEquals(AclType.my_algos.acl_string, 'algo://.my/*')
        self.assertEquals(AclType.public.acl_string, 'user://*')
        self.assertEquals(AclType.default, AclType.my_algos)

    def test_from_acl_response(self):
        self.assertEquals(AclType.from_acl_response([]), AclType.private)
        self.assertEquals(AclType.from_acl_response(['algo://.my/*']), AclType.my_algos)
        self.assertEquals(AclType.from_acl_response(['user://*']), AclType.public)

if __name__ == '__main__':
    unittest.main()
