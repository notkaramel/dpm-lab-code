from utils.remote import BUSY_WAITING, Connection, Command, Message, RemoteBrick, RemoteBrickServer, RemoteClient, socket, DEFAULT_PORT, _MethodCaller, _RemoteCaller
from utils import dummy, brick
import unittest
import time
import threading
from collections import deque
import uuid

DEFAULT_PORT = 2111
_RemoteCaller.TESTING = True

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
        self.buffer = deque()

    def send(self, obj):
        self.other.buffer.append(obj)

    def recv(self, num_bytes):
        while len(self.buffer) <= 0:
            time.sleep(0.1)

        return self.buffer.popleft()


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

    def test_performance(self):
        avg = 0
        N = 100
        s1, s2 = FakeSocket.create_pair()

        for i in range(100):
            start = time.perf_counter_ns()
            s1.send('bob')
            o = s2.recv(0)
            end = time.perf_counter_ns()
            avg += (end - start)

        self.assertGreater(1, avg / N / 1e9)


class TestConnection(unittest.TestCase):
    def setUp(self):
        port = DEFAULT_PORT
        s1, s2 = FakeSocket.create_pair()
        self.conn1 = Connection(s1)
        self.conn2 = Connection(s2)

    def test_01(self):
        m = "Hello"
        tst = {}

        def listener(obj, conn):
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
        tst = {'data': []}

        def listener(obj, conn):
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

    def test_performance(self):
        avg = 0
        N = 20
        d = []

        def listener(obj, conn):
            d.append(obj)
        self.conn2.register_listener("messages", listener)
        for i in range(N):
            start = time.perf_counter_ns()
            self.conn1.send(Message('hi'))
            while not d:
                time.sleep(0.001)
                pass
            end = time.perf_counter_ns()
            d.clear()
            avg += (end - start)

        self.assertGreater(1, avg / N / 1e9)
        # print(f'average Connection send-recv time was {avg / N / 1e9}')


class TestRemoteBrick(unittest.TestCase):
    def setUp(self):
        s1, s2 = FakeSocket.create_pair()
        self.rem1 = RemoteBrick("0.0.0.0", None, sock=s1)
        self.rem2 = RemoteBrick("0.0.0.0", None, sock=s2)

    def test_01(self):
        m = "Hey there buddy"
        self.rem1.send_message(m)

        # for i in range(10):
        while True:
            time.sleep(0.1)
            if self.rem2.num_messages() > 0:
                break

        self.assertEqual(m, self.rem2.get_message())

    def test_02(self):
        func = 'verify'
        args = ['a', 'b', 'c']
        kwargs = {'name': 'bob', 'age': 10}
        cid = self.rem1._send_command(
            func, *args, wait_for_data=False, **kwargs)

        res = self.rem2._get_result(cid, wait_for_data=True)

        self.assertNotEqual(None, res)
        self.assertEqual(res.func_name, func)
        self.assertEqual(res.id, cid)

    def test_performance(self):
        avg = 0
        N = 20

        for i in range(N):
            start = time.perf_counter_ns()

            cid = self.rem1._send_command('verify', wait_for_data=False)
            res = self.rem2._get_result(cid, wait_for_data=True)

            end = time.perf_counter_ns()
            avg += (end - start)

        self.assertGreater(1, avg / N / 1e9)
        # print(f'average Connection send-recv time was {avg / N / 1e9}')


class TestIntegrationRemoteBrick(unittest.TestCase):
    def _thread_func(self):
        self.server = socket.create_server(('0.0.0.0', DEFAULT_PORT))
        conn, addr = self.server.accept()
        self.s2 = conn

    def setUp(self):
        t = threading.Thread(
            target=TestIntegrationRemoteBrick._thread_func, args=(self,), daemon=True)
        t.start()
        time.sleep(BUSY_WAITING)
        self.s2 = None
        self.s1 = socket.create_connection(('127.0.0.1', DEFAULT_PORT))
        for i in range(8):
            time.sleep(0.1)
            if self.s2 is not None:
                break
        self.assertNotEqual(None, self.s1)
        self.assertNotEqual(None, self.s2)

        self.rem1 = RemoteBrick('127.0.0.1', None, sock=self.s1)
        self.rem2 = RemoteBrick('127.0.0.1', None, sock=self.s2)

    def test_01(self):
        m = "Hey there buddy"
        self.rem1.send_message(m)

        # for i in range(10):
        while True:
            time.sleep(0.1)
            if self.rem2.num_messages() > 0:
                break
        received = self.rem2.get_message()
        self.assertEqual(m, received)

    def test_02(self):
        func = 'verify'
        args = ['a', 'b', 'c']
        kwargs = {'name': 'bob', 'age': 10}
        cid = self.rem1._send_command(
            func, *args, wait_for_data=False, **kwargs)

        res = self.rem2._get_result(cid, wait_for_data=True)

        self.assertNotEqual(None, res)
        self.assertEqual(res.func_name, func)
        self.assertEqual(res.id, cid)

    def test_performance(self):
        avg = 0
        N = 100

        for i in range(N):
            start = time.perf_counter_ns()

            cid = self.rem1._send_command('verify', wait_for_data=False)
            res = self.rem2._get_result(cid, wait_for_data=True)

            end = time.perf_counter_ns()
            avg += (end - start)

        self.assertGreater(1, avg / N / 1e9)
        # print(f'average Connection send-recv time for sockets was {avg / N / 1e9}')

    def tearDown(self):
        self.server.close()
        self.rem1.close()
        self.rem2.close()


class _FakeRemoteBP:
    def action1(self, a1, a2, a3=None):
        return (a1, a2, a3)


class TestRemoteBrickServer(unittest.TestCase):
    def setUp(self) -> None:
        self.server = RemoteBrickServer(password='password', port=DEFAULT_PORT)
        self.fake = _FakeRemoteBP()
        self.server.register_object(self.fake)
        self.conn1 = RemoteBrick('127.0.0.1', 'password', port=DEFAULT_PORT)
        self.conn2 = RemoteBrick('127.0.0.1', 'password', port=DEFAULT_PORT)
        RemoteClient.TESTING = True

    def test_01(self):
        res = self.conn1._send_command('__verify', wait_for_data=1)
        self.assertNotEqual(None, res)
        self.assertEqual(
            f"I am sending back the command for {res.id}", res.result)

    def test_02(self):
        res = self.conn1._send_command('__verify', wait_for_data=1)
        self.assertNotEqual(None, res)
        self.assertEqual(
            f"I am sending back the command for {res.id}", res.result)

        res = self.conn2._send_command('__verify', wait_for_data=1)
        self.assertNotEqual(None, res)
        self.assertEqual(
            f"I am sending back the command for {res.id}", res.result)

    def test_03(self):
        res = self.conn1._send_command('action1', 1, 2, wait_for_data=1, a3=45)
        self.assertNotEqual(None, res)
        self.assertEqual((1, 2, 45), res.result)
        res = self.conn2._send_command('action1', wait_for_data=1)
        err = None
        try:
            self.fake.action1()
        except Exception as e:
            err = str(e)
        self.assertNotEqual(None, res)
        self.assertEqual(err, res.result)

    def test_performance(self):
        avg = 0
        N = 1

        for i in range(N):
            start = time.perf_counter_ns()

            cid = self.conn1._send_command('__verify', wait_for_data=1)

            end = time.perf_counter_ns()
            avg += (end - start)

        self.assertGreater(1, avg / N / 1e9)
        # print(
        #     f'average Connection send-recv time for brick-server was {avg / N / 1e9}')

    def tearDown(self) -> None:
        RemoteClient.TESTING = False
        self.server.close()
        self.conn1.close()
        self.conn2.close()


class TestRemoteCaller(unittest.TestCase):
    class FakeRemoteBrick:
        def __init__(self):
            self.command = None

        def _send_command(self, func, *args, wait_for_data=True, **kwargs):
            self.command = Command(
                func, *args, wait_for_data=wait_for_data, **kwargs)
            return self.command

    def setUp(self) -> None:
        self.fake = TestRemoteCaller.FakeRemoteBrick()
        self.obj: dummy.Brick = _RemoteCaller.create_caller(
            dummy.Brick(), self.fake)

    def test_01(self):
        # The method that goes through _RemoteCaller
        c = self.obj.get_sensor('Fake Port 1')
        self.assertNotEqual(None, c)  # Checking that there is output
        # print(c, self.fake.command)
        self.assertEqual(c, self.fake.command)  # Checking equivavlence


class TestRemoteCallerIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.fake = TestRemoteCaller.FakeRemoteBrick()
        self.obj: dummy.Brick = _RemoteCaller.create_caller(
            brick.Brick(), self.fake)

    def test_01(self):
        ultra = brick.EV3UltrasonicSensor(1)
        ultra.brick = self.obj
        c = ultra.get_raw_value()
        self.assertNotEqual(None, c)
        self.assertEqual(c, self.fake.command)
        self.assertTrue(isinstance(c, Command))

    def test_02(self):
        ultra = brick.EV3UltrasonicSensor(1)
        brick.restore_default_brick(self.obj)
        c = ultra.get_raw_value()
        self.assertEqual(None, c)

    def test_03(self):
        brick.restore_default_brick(self.obj)
        ultra = brick.EV3UltrasonicSensor(1)
        c = ultra.get_raw_value()
        self.assertNotEqual(None, c)
        self.assertEqual(c, self.fake.command)
        self.assertTrue(isinstance(c, Command))


class TestRemoteBrickSystemTest(unittest.TestCase):
    class FakeBP():
        def get_sensor(self, *args, **kwargs) -> str:
            return "You got me! The sensor!"
        def set_sensor_type(self, *args, **kwargs) -> None:
            return None

    def setUp(self) -> None:
        self.answer = TestRemoteBrickSystemTest.FakeBP()
        brick.restore_default_brick(self.answer)
        self.remote_brick_server = RemoteBrickServer(
            "password", port=DEFAULT_PORT)  # Actual Remote BrickServer
        self.remote_brick = RemoteBrick(
            "127.0.0.1", "password", port=DEFAULT_PORT)

    def test_01(self):
        res = self.remote_brick.get_brick().get_sensor(1)
        self.assertNotEqual(None, res)
        self.assertEqual(self.answer.get_sensor(), res.result)
    def test_01_01(self):
        _RemoteCaller.TESTING = False
        res = self.remote_brick.get_brick().get_sensor(1)
        _RemoteCaller.TESTING = True
        self.assertNotEqual(None, res)
        self.assertEqual(self.answer.get_sensor(), res)

    def test_02(self):
        sensor = self.remote_brick.make_remote(brick.EV3UltrasonicSensor, 1)
        res = sensor.get_value()
        self.assertNotEqual(None, res)
        self.assertEqual(self.answer.get_sensor(), res.result)

    def tearDown(self) -> None:
        brick.restore_default_brick()  # For the fake_server_brick setting
        self.remote_brick.close()
        self.remote_brick_server.close()


if __name__ == '__main__':
    unittest.main()
