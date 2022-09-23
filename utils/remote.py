from math import inf
import socket
import sys
import threading
import time
from collections import deque
from typing import List

import json
import marshal
import pickle  # using one of these three to parse data for sending

from . import brick
from . import dummy

TIMEOUT = socket.getdefaulttimeout()
DEFAULT_PORT = 2110
THREAD_SLEEP = 0.001
BUSY_WAITING = 0.001
DEFAULT_PASSWORD = 'password'
SERVER_START_RETRIES = 5
DEBUG_DEFAULT = False


class IdentifyingException(Exception):
    def __repr__(self):
        return f'{self.__class__.__name__}: {super(IdentifyingException, self).__repr__()}'


class UnsupportedCommand(IdentifyingException):
    pass


class brickle:
    _parser = marshal

    class UnpicklingError(IdentifyingException):
        pass

    def dumps(obj):
        try:
            res = {}
            if isinstance(obj, PasswordProtected):
                res = brickle._dumps(obj)
            else:
                pass
            return brickle._parser.dumps(res)
        except Exception as err:
            raise brickle.UnpicklingError(err)

    def _dumps(obj):
        res = vars(obj).copy()
        res['__class__'] = obj.__class__.__name__
        return res

    def loads(data):
        try:
            data = brickle._parser.loads(data)
            if data['__class__'] == 'Command':
                c = Command(data['func_name'])
                return brickle._loads(c, data)
            elif data['__class__'] == 'Message':
                m = Message(data['text'])
                return brickle._loads(m, data)
            else:
                return None
        except Exception as err:
            raise brickle.UnpicklingError(err)

    def _loads(obj, data):
        # Specific to this implementation
        del data['__class__']
        obj.__dict__.update(data)
        return obj


class PasswordProtected:
    def __init__(self, password=None):
        if password is None:
            password = DEFAULT_PASSWORD
        self.password = password

    def verify_password(self, test):
        return test == self.password


class Message(PasswordProtected):
    def __init__(self, text):
        super(Message, self).__init__()
        self.text = text

    def __repr__(self):
        return self.text


class Command(PasswordProtected):
    def __init__(self, func_name, *args, **kwargs):
        super(Command, self).__init__()
        self.func_name = func_name
        self.args = args
        self.kwargs = kwargs
        self.id = id(self)
        self.result = None

    def __repr__(self):
        return f"{self.id}: {self.func_name}({self.args},{self.kwargs})"


class Debuggable:
    DEBUG_ALL = {}
    DEBUG_COUNTER = 0

    def __init__(self, debug=None):
        self.debug = DEBUG_DEFAULT if debug is None else debug
        if self.debug:
            i = id(self)
            if i not in self.__class__.DEBUG_ALL:
                self.__class__.DEBUG_ALL[i] = f'{self.__class__.__name__}{self.__class__.DEBUG_COUNTER}'
                self.__class__.DEBUG_COUNTER += 1

    def _debug(self, text):
        if self.debug:
            i = self.__class__.DEBUG_ALL[id(self)]
            print(f'>>> ({i}) {text}\t', file=sys.stderr)


class ConnectionError(IdentifyingException):
    pass


class ConnectionFatalError(IdentifyingException):
    pass


class Connection:
    def __init__(self, sock, password="password", debug=None):
        self.sock: socket.socket = sock
        self.listeners = {}
        self.run_event = threading.Event()
        self.lock_listener = threading.Lock()
        self.lock_send = threading.Lock()
        self._isclosed = False

        self.password = password
        self.run_event.set()
        t = threading.Thread(target=Connection._func,
                             args=(self,), daemon=True)
        t.start()

    def _func(self):
        # self._debug('starting connection thread')
        while self.run_event.is_set():
            try:
                # self._debug('start receiving')
                d = self.sock.recv(4096)
                # self._debug('received. loading...')
                o = brickle.loads(d)
                # self._debug('received. loaded...')

                self.lock_listener.acquire()

                if isinstance(o, PasswordProtected) and o.verify_password(self.password):
                    for key, val in self.listeners.items():
                        listener, args = val
                        try:
                            # self._debug(f'running listener "{key}"')
                            listener(*args, o, self)
                            # self._debug(f'completed listener "{key}"')
                        except Exception as err:
                            c = ConnectionError(
                                f"Error: Listener {key} - {err} {val}")
                            print(c, file=sys.stderr)
                self.lock_listener.release()
            except OSError as err:
                if self.isclosed():
                    return
                print('Warning:', err, file=sys.stderr)
            except brickle.UnpicklingError as err:
                print('Data Unpickling Error:', err, file=sys.stderr)
            except Exception as err:
                c = ConnectionFatalError(f'Bad Error: {err}')
                print(c, file=sys.stderr)
        # self._debug(f'connection thread ended')

    def send(self, obj):
        if isinstance(obj, PasswordProtected):
            self.lock_send.acquire()
            obj.password = self.password
            # self._debug(f'dumping data ({str(obj)})')
            d = brickle.dumps(obj)
            # self._debug(f'sending data dump ({str(obj)})')
            self.sock.send(d)
            # self._debug(f'data sent ({str(obj)})')
            self.lock_send.release()

    def register_listener(self, name, listener, args=None):
        """Expects a listener of function type:
        def func(obj)

        where obj is the unpickled object, at the time
        """
        if args is None:
            args = tuple()

        self.lock_listener.acquire()
        self.listeners[name] = (listener, args)
        self.lock_listener.release()

    def __del__(self):
        self.close()

    def close(self):
        try:
            self.run_event.clear()
            self.sock.shutdown()
            self.sock.close()
        except:
            pass

        self._isclosed = True

    def isclosed(self):
        return self._isclosed


class MethodCallerException(IdentifyingException):
    pass


class _MethodCaller:
    def __init__(self, obj):
        self.cls = obj.__class__
        self.obj = obj
        self.methods = {func_name: getattr(self.cls, func_name) for func_name in dir(
            self.cls) if callable(getattr(self.cls, func_name)) and not func_name.startswith("__")}

    def supports_command(self, command: Command):
        return command.func_name in self.methods

    def execute(self, command: Command):
        if command.func_name in self.methods:
            try:
                command.result = self.methods[command.func_name](self.obj,
                                                                 *command.args, **command.kwargs)
            except Exception as err:
                command.result = str(MethodCallerException(err))
        return command


class MessageReceiver(object):  # Somewhat abstract class that needs self.conn
    def __init__(self):
        self.messages = deque()
        self.lock_messages = threading.Lock()

    def num_messages(self):
        self.lock_messages.acquire()
        r = len(self.messages)
        self.lock_messages.release()
        return r

    def get_messages(self, count=0):
        """Gets the specified number of messages from the message buffer.
        Thread-safe.
        """
        # Receiving messages in the listener thread for this RemoteBrick socket
        self.lock_messages.acquire()

        result = []
        if count <= 0:
            result = list(self.messages)
            self.messages.clear()
        elif count > 0:
            count = min(len(self.messages), count)
            for i in range(count):
                result.append(self.messages.popleft())

        self.lock_messages.release()
        return result

    def get_message(self):
        m = self._get_message()
        return str(m) if m is not None else m

    def _get_message(self):
        """Gets the one message from the message buffer, or None if none present.
        Thread-safe.
        """
        self.lock_messages.acquire()
        try:
            m = self.messages.popleft()
        except:
            m = None
        self.lock_messages.release()
        return m


class _RemoteCaller:
    def create_caller(obj, remote_brick):
        caller = _RemoteCaller(remote_brick)

        for name in dir(obj):
            attr = getattr(obj, name)
            if callable(attr) and not name.startswith('__'):
                setattr(obj, name, caller._generate(name))

        obj.__remote__ = caller
        return obj

    def __init__(self, remote_brick):
        self.remote_brick = remote_brick

    def _generate(self, func_name):
        def func(*args, wait_for_data=60, **kwargs):
            return self.remote_brick._send_command(func_name, *args, wait_for_data=wait_for_data, **kwargs)
        return func


class RemoteBrick(MessageReceiver):
    def __init__(self, address, password, sock=None):
        super(RemoteBrick, self).__init__()
        self._brick = _RemoteCaller.create_caller(dummy.Brick(), self)
        self.buffer = {}
        self.lock_buffer = threading.Lock()

        self.status = None

        if sock is None:
            self.sock = socket.create_connection((address, DEFAULT_PORT))
        else:
            self.sock = sock

        self.conn = Connection(self.sock, password)
        self.address = address
        self.password = self.conn.password

        self.conn.register_listener('main', RemoteBrick._listener, (self,))

    def send_message(self, text):
        self.conn.send(Message(text))

    def make_remote(self, sensor_or_motor: type, *args) -> brick.Sensor | brick.Motor:
        """Creates a remote sensor or motor that is attached to the remote brick.
        sensor_or_motor - A class, such as Motor or EV3UltrasonicSensor
        *args - any of the normal arguments that would be used to create the object locally

        Returns None if you gave the wrong class.
        """
        if sensor_or_motor == brick.Sensor or sensor_or_motor == brick.Motor:
            return sensor_or_motor(*args, bp=self._brick)
        return None

    def set_default_brick(self):
        """Sets this RemoteBrick to be the default brick for all newly initialized motors or sensors.
        Use brick.restore_default_brick() to reset back to normal.

        This will only apply to newly created devices.

        Normal defined as:
        - The useless dummy brick on PCs
        - The actual BrickPi itself, if running this code on the BrickPi
        """
        brick.BP = self._brick

    def __del__(self):
        self.close()

    def close(self):
        try:
            self.conn.close()
        except:
            pass

    def _listener(self, obj, conn):
        if isinstance(obj, Message):
            self.lock_messages.acquire()
            self.messages.append(obj)
            self.lock_messages.release()
        elif isinstance(obj, Command):
            self.lock_buffer.acquire()
            self.buffer[obj.id] = obj
            self.lock_buffer.release()
        else:
            pass

    def _send_command(self, func, *args, wait_for_data=True, **kwargs):
        """Send a command object to the other brick.
        Thread-safe.
        """
        c = Command(func, * args, **kwargs)
        self.conn.send(c)
        if wait_for_data:
            return self._get_result(c.id, wait_for_data)
        else:
            return c.id

    def _get_result(self, cid, wait_for_data=True) -> Command:
        """Get the result of the following command id.
        Thread-safe.
        """
        waiting = not not wait_for_data
        if not isinstance(wait_for_data, (int, float)):
            wait_for_data = inf

        start = time.perf_counter()
        end = time.perf_counter()
        while waiting and wait_for_data > (end-start):
            self.lock_buffer.acquire()
            if cid in self.buffer:
                self.lock_buffer.release()
                break
            self.lock_buffer.release()

            time.sleep(BUSY_WAITING)
            end = time.perf_counter()

        self.lock_buffer.acquire()
        o = self.buffer.get(cid, None)
        self.lock_buffer.release()
        return o


class RemoteBrickServer(MessageReceiver):
    def __init__(self, port=None, password=None):
        super(RemoteBrickServer, self).__init__()

        self._caller = _MethodCaller(brick.BP)

        self._isclosed = False

        self.connections: List[RemoteBrick] = []
        self.password = DEFAULT_PASSWORD if password is None else password

        self.commands = []

        self.lock_commands = threading.Lock()

        self.port = (DEFAULT_PORT if port is None else port)

        self.lock_connections = threading.Lock()
        self.run_event = threading.Event()

        self.run_event.set()

        self.t1 = threading.Thread(target=self._thread_server)
        self.t1.start()

    def _thread_server(self):
        retries = SERVER_START_RETRIES
        while self.run_event.is_set():
            try:
                self.sock.close()
            except:
                pass  # Make sure it's closed before recreating the server

            try:
                self.sock = socket.create_server(('0.0.0.0', self.port))
            except OSError as err:
                if retries <= 0:
                    return
                print('Server Creation Error:', err, file=sys.stderr)
                retries -= 1
                continue
            retries = SERVER_START_RETRIES
            while self.run_event.is_set():
                try:
                    conn, addr = self.sock.accept()  # blocking, don't need time sleep
                except OSError as err:
                    if retries <= 0 or self.isclosed():
                        return
                    print('Warning:', err, file=sys.stderr)
                    break  # go for retrying the server creation

                self.lock_connections.acquire()
                connection = Connection(conn, self.password)
                connection.register_listener(
                    'main', self._thread_listener)
                self.connections.append(connection)
                self.lock_connections.release()
                if not self.run_event.is_set():
                    self.sock.close()
                    break

    def _thread_listener(self, obj, conn):
        if isinstance(obj, Command):
            self.lock_commands.acquire()
            self.execute(conn, obj)
            self.lock_commands.release()
        if isinstance(obj, Message):
            self.lock_messages.acquire()
            self.messages.append(obj)
            self.lock_commands.release()

    def execute(self, conn: Connection, command: Command):
        """Executes a command and sends the result back to the remote brick (rem)"""
        if self._caller.supports_command(command):
            self._caller.execute(command)
            conn.send(command)
        elif command.func_name == '__initialize':
            pass
        elif command.func_name == '__verify':
            command.result = (
                f"I am sending back the command for {command.id}")
            conn.send(command)
        else:
            command.result = str(UnsupportedCommand(
                f"Command '{command.func_name}' is not supported."))

    def __del__(self):
        self.close()

    def close(self):
        self._isclosed = True
        self.run_event.clear()
        self.lock_connections.acquire()
        c = self.connections
        self.connections = []
        self.lock_connections.release()
        for conn in c:
            conn.close()
        self.sock.close()

    def isclosed(self):
        return self._isclosed
