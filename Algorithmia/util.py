def getParentAndBase(path):
    pieces = path.split('/')
    if len(pieces) < 2:
        raise Exception('Invalid path')

    base = None
    parent = None
    for index in range(len(pieces)):
        cur = pieces[len(pieces) - (index + 1)]

        if base is None:
            if len(cur) > 0:
                base = cur
        elif parent is None:
            if len(cur) > 0:
                parent = cur
        else:
            parent = cur + '/' + parent

    if not parent or not base:
        raise Exception('Invalid path')

    return parent, base

def pathJoin(parent, base):
    if parent.endswith('/'):
        return parent + base
    return parent + '/' + base