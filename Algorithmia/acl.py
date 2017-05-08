class Acl(object):
    def __init__(self, read_acl):
        self.read_acl = read_acl

    @staticmethod
    def from_acl_response(acl_response):
        '''Takes JSON response from API and converts to ACL object'''
        if 'read' in acl_response:
            read_acl = AclType.from_acl_response(acl_response['read'])
            return Acl(read_acl)
        else:
            raise ValueError('Response does not contain read ACL')

    def to_api_param(self):
        read_acl_string = self.read_acl.acl_string
        if read_acl_string is None:
            return {'read':[]}
        return {'read':[read_acl_string]}

class AclInner(object):
    def __init__(self, pseudonym, acl_string):
        self.pseudonym = pseudonym
        self.acl_string = acl_string

    def __repr__(self):
        return 'AclType(pseudonym=%s,acl_string=%s)' % (self.pseudonym, self.acl_string)

class AclType(object):
    public = AclInner('public','user://*')
    my_algos = AclInner('my_algos','algo://.my/*')
    private = AclInner('private',None)  # Really is an empty list
    default = my_algos

    types = (public, my_algos, private)

    @staticmethod
    def from_acl_response(acl_list):
        if len(acl_list) == 0:
            return AclType.private
        else:
            acl_string = acl_list[0]
            for t in AclType.types:
                if t.acl_string == acl_string:
                    return t
            else:
                raise ValueError('Invalid acl string %s' % (acl_list[0]))

class ReadAcl(object):
    public = Acl(AclType.public)
    private = Acl(AclType.private)
    my_algos = Acl(AclType.my_algos)
