import sys
# look in ../ BEFORE trying to import Algorithmia.  If you append to the
# you will load the version installed on the computer.
sys.path = ['../'] + sys.path

import unittest
import Algorithmia
from Algorithmia.acl import AclType, Acl, ReadAcl
from Algorithmia.datadirectory import DataDirectory

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

    def test_create_acl(self):
        c = Algorithmia.client()
        dd = DataDirectory(c, 'data://.my/privatePermissions')
        if dd.exists():
            dd.delete(True)
        dd.create(ReadAcl.private)

        dd_perms = DataDirectory(c, 'data://.my/privatePermissions').get_permissions()
        self.assertEquals(dd_perms.read_acl, AclType.private)

        dd.update_permissions(ReadAcl.public)
        dd_perms = DataDirectory(c, 'data://.my/privatePermissions').get_permissions()
        self.assertEquals(dd_perms.read_acl, AclType.public)

if __name__ == '__main__':
    unittest.main()
