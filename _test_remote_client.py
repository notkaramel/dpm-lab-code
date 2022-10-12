from utils import remote, brick

class List(list):
    CUSTOM=[
        '__len__',
        '__contains__',
        '__getitem__',
        '__setitem__',
        '__repr__',
        '__str__'
    ]

    def __len__(self):
        return self.__len__()
    def __contains__(self, key):
        return self.__contains__(key)
    def __getitem__(self, key):
        return self.__getitem__(key)
    def __setitem__(self, key, value):
        return self.__setitem__(key, value)
    def __repr__(self):
        return self.__repr__()
    def __str__(self):
        return self.__str__()

if __name__=='__main__':
    # client = remote.RemoteBrick("127.0.0.1", "password")

    client = remote.RemoteClient('127.0.0.1', 'password')

    ls = List()

    remote_ls = client.create_caller(ls, custom=List.CUSTOM, var_name='ls')
