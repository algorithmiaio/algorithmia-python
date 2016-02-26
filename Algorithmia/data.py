from enum import Enum

DataObjectType = Enum('DataObjectType','file directory')

class DataObject(object):
    def __init__(self, data_object_type):
        self.data_object_type = data_object_type

    def is_file(self):
        '''Returns whether object is a file'''
        return self.data_object_type is DataObjectType.file

    def is_dir(self):
        '''Returns whether object is a directory'''
        return self.data_object_type is DataObjectType.directory

    def get_type(self):
        '''Returns type of this DataObject'''
        return self.data_object_type

    def set_attributes(self):
        '''Sets attributes about the directory after querying the Data API'''
        raise NotImplementedError