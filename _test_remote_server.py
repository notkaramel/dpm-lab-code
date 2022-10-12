from utils import remote, brick
from _test_remote_client import List
# server = remote.RemoteBrickServer("password")
# input(">>> Press Enter to End the Server")

if __name__=='__main__':
    server = remote.RemoteServer('password')

    ls = []
    server.register_object(ls, custom=List.CUSTOM, var_name='ls')

