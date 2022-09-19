from utils.remote import Connection, Command, Message, RemoteBrick, socket
import unittest
import time


class FakeSocket:
    @staticmethod
    def create_pair():
        sock1 = FakeSocket()
        sock2 = FakeSocket()
        sock1.other = sock2
        sock2.other = sock1
        return sock1, sock2

    def __init__(self):
        self.other: FakeSocket = None
        self.buffer = []

    def send(self, obj):
        self.other.buffer.append(obj)

    def recv(self, num_bytes):
        while len(self.buffer) <= 0:
            time.sleep(0.1)

        o = self.buffer[0]
        del self.buffer[0]
        return o


class TestFakeSocket(unittest.TestCase):
    def test_01(self):
        s1, s2 = FakeSocket.create_pair()
        self.assertEqual(s1, s2.other)
        self.assertEqual(s1.other, s2)
        s1.send('bob')
        o = s2.recv(0)
        self.assertEqual('bob', o)
        s2.send('charlie')
        o = s1.recv(1)
        self.assertEqual('charlie', o)


class TestConnection(unittest.TestCase):
    def setUp(self):
        port = 2110
        s1, s2 = FakeSocket.create_pair()
        self.conn1 = Connection(s1)
        self.conn2 = Connection(s2)

    def test_01(self):
        m = "Hello"
        tst = {}

        def listener(obj):
            if isinstance(obj, Message):
                tst['data'] = obj.text
        self.conn2.register_listener("messages", listener)
        self.conn1.send(Message(m))

        for i in range(5):
            time.sleep(0.1)
            if 'data' in tst:
                break

        self.assertEqual(m, tst.get('data'))

    def test_02(self):
        m = "Hello"
        tst = {'data':[]}

        def listener(obj):
            if isinstance(obj, Message):
                tst['data'].append(obj.text)
        self.conn2.register_listener("messages", listener)
        
        for i in range(10):
            self.conn1.send(Message(m))

        for i in range(5):
            time.sleep(0.1)
            if len(tst['data']) >= 8:
                break

        for dat in tst.get('data'):
            self.assertEqual(m, dat)


class TestRemoteBrick(unittest.TestCase):
    def setUp(self):
        s1, s2 = FakeSocket.create_pair()
        self.rem1 = RemoteBrick("", None, sock=s1)
        self.rem2 = RemoteBrick("", None, sock=s2)
    
    def test_01(self):
        m = "Hey there buddy"
        self.rem1.send_message(m)

        # for i in range(10):
        while True:
            time.sleep(0.1)
            if self.rem2.num_messages() > 0:
                break
            
        self.assertEqual(m, self.rem2.get_message())

if __name__ == '__main__':
    unittest.main()
