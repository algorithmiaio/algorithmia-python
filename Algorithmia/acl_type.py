class AclInner(object):
    def __init__(self, pseudonym, acl_string):
        self.acl_string = acl_string
        self.pseudonym = pseudonym
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
