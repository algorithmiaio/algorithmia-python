import os

def getParentAndBase(path):
    parent, base = os.path.split(path)
    while not base:
        if not parent:
            raise Exception('Invalid directory path')
        parent, base = os.path.split(parent)

    if not parent:
            raise Exception('Invalid directory path')

    return parent, base