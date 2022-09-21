import socket
import pickle
import sys
import threading
import time
from collections import deque
from typing import List

from . import brick

TIMEOUT = socket.getdefaulttimeout()
DEFAULT_PORT = 2110
THREAD_SLEEP = 0.100
BUSY_WAITING = 0.100
DEFAULT_PASSWORD = 'password'
SERVER_START_RETRIES = 5


class PasswordProtected:
    def __init__(self, password=None):
        if password is None:
            password = DEFAULT_PASSWORD
        self.password = password

    def verify_password(self, test):
        return test == self.password


class Message(PasswordProtected):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text


class Command(PasswordProtected):
    def __init__(self, func_name, *args, **kwargs):
        self.func_name = func_name
        self.args = args
        self.kwargs = kwargs
        self.id = id(self)
        self.result = None

    def __repr__(self):
        return f"{self.id}: {self.func_name}({self.args},{self.kwargs})"


class Connection:
    def __init__(self, sock, password="password"):
        self.sock: socket.socket = sock
        self.listeners = {}
        self.run_event = threading.Event()
        self.lock_listener = threading.Lock()
        self._status = None

        self.password = password
        self.run_event.set()
        t = threading.Thread(target=Connection._func,
                             args=(self,), daemon=True)
        t.start()

    def _func(self):
        self._status = True
        while self.run_event.is_set():
            try:
                o = pickle.loads(self.sock.recv(4096))
                self.lock_listener.acquire()

                if isinstance(o, PasswordProtected) and o.verify_password(self.password):
                    for key, val in self.listeners.items():
                        listener, args = val
                        try:
                            listener(*args, o, self)
                        except Exception as err:
                            print(f"Error: Listener {key} - {err}", val)
                self.lock_listener.release()
            except Exception as err:
                print(err)

    def send(self, obj):
        if isinstance(obj, PasswordProtected):
            obj.password = self.password
            self.sock.send(pickle.dumps(obj))

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
            self.sock.shutdown()
            self.sock.close()
        except:
            pass

class MessageSender(object): # Somewhat abstract class that needs self.conn
    def __init__(self):
        self.messages = deque()
        self.lock_messages = threading.Lock()
        self.conn: Connection = None
    
    def send_message(self, text):
        self.conn.send(Message(text))

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
        """Gets the one message from the message buffer, or None if none present.
        Thread-safe.
        """
        m = self.get_messages(1)
        if type(m) == list and len(m) > 0:
            return str(m[0])
        else:
            return None


class RemoteBrick(MessageSender):
    def __init__(self, address, password, sock=None):
        super(RemoteBrick, self).__init__()
        self.buffer = {}
        self.lock_buffer = threading.Lock()

        self.status = None

        if sock is None:
            self.sock = socket.create_connection(
                (address, DEFAULT_PORT), TIMEOUT)
        else:
            self.sock = sock

        self.conn = Connection(sock, password)
        self.address = address
        self.password = self.conn.password

        self.conn.register_listener('main', RemoteBrick._listener, (self,))

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
        if isinstance(wait_for_data, (int, float)):
            wait_for_data /= BUSY_WAITING
            wait_for_data = int(wait_for_data)

        while wait_for_data:
            if type(wait_for_data) == int:
                wait_for_data = min(wait_for_data - 1, 0)

            self.lock_buffer.acquire()
            if cid in self.buffer:
                break
            self.lock_buffer.release()

            time.sleep(BUSY_WAITING)

        self.lock_buffer.acquire()
        o = self.buffer.get(cid, None)
        self.lock_buffer.release()
        return o


class RemoteBrickOld(object):
    def __init__(self, address, password="password", sock=None):
        self.messages = []
        self.buffer = {}
        self.lock_message = threading.Lock()
        self.lock_buffer = threading.Lock()
        self.lock_sock = threading.Lock()
        self.run_event = threading.Event()
        self._status = None

        self.address = address
        self.password = password

        if sock is None:
            self.sock = socket.create_connection(
                (self.address, DEFAULT_PORT), TIMEOUT)
        else:
            self.sock = sock

        self.thread = threading.Thread(
            target=RemoteBrick._thread_func, args=(self,), daemon=True)

    def _thread_func(self):
        self._status = True
        while self.run_event.is_set():
            try:
                o = pickle.loads(self.sock.recv(4096))
                if isinstance(o, Message):
                    self.lock_message.acquire()
                    self.messages.append(o)
                    self.lock_message.release()
                elif isinstance(o, Command):
                    self.lock_buffer.acquire()
                    self.buffer[o.cid] = o
                    self.lock_buffer.release()
                else:
                    pass
            except socket.error as err:
                self._status = err
                break
            except pickle.UnpicklingError as err:
                self._status = err

            time.sleep(THREAD_SLEEP)
        self.sock.shutdown()
        self.sock.close()
        if self._status is True:
            self._status = False

    def _send(self, data):
        self.lock_sock.acquire()
        self.sock.send(data)
        self.lock_sock.release()

    def __del__(self):
        try:
            self.sock.shutdown()
            self.sock.close()
        except:
            pass

    def get_remote_status(self):
        if self._status is None:
            return "Unstarted"
        elif self._status is True:
            return "Running"
        elif self._status is False:
            return "Stopped"
        else:
            return f"Error: {self._status}"

    def send_message(self, text):
        self._send(pickle.dumps(Message(text, self.password)))

    def get_messages(self, count=0):
        """Gets the specified number of messages from the message buffer.
        Thread-safe.
        """
        # Receiving messages in the listener thread for this RemoteBrick socket
        self.lock_message.acquire()

        result = []
        if count <= 0:
            result = self.messages.copy()
            self.messages.clear()
        elif count > 0 and len(self.messages) >= count:
            result = self.messages[:count]
            for i in range(count):
                del self.messages[0]

        self.lock_message.release()
        return result

    def get_message(self):
        """Gets the one message from the message buffer, or None if none present.
        Thread-safe.
        """
        m = self.get_messages(1)
        if type(m) == list and len(m) > 0:
            return m[0]
        else:
            return None

    def _send_command(self, func, *args, wait_for_data=True, **kwargs):
        """Send a command object to the other brick.
        Thread-safe.
        """
        c = Command(func, self.password ** args, **kwargs)
        self._send(pickle.dumps(c))
        return self._get_result(c.id, wait_for_data)

    def _get_result(self, cid, wait_for_data=True):
        """Get the result of the following command id.
        Thread-safe.
        """

        self.lock_buffer.acquire()
        while wait_for_data and cid not in self.buffer:
            self.lock_buffer.release()
            time.sleep(BUSY_WAITING)
            self.lock_buffer.acquire()

        o = self.buffer.get(cid, None)
        self.lock_buffer.release()
        return o


class RemoteBrickServer(MessageSender):
    def __init__(self, port=None, password=None):
        super(RemoteBrickServer, self).__init__()

        self.connections: List[RemoteBrick] = []
        self.password = DEFAULT_PASSWORD if password is None else password

        self.commands = []

        self.lock_commands = threading.Lock()

        self.port = (DEFAULT_PORT if port is None else port)

        self.lock_connections = threading.Lock()
        self.run_event = threading.Event()

        self.run_event.set()

        self.t1 = threading.Thread(target=self._thread_server, args=(self,))
        self.t1.start()

    def _thread_server(self):
        retries = SERVER_START_RETRIES
        while self.run_event.is_set():
            try:
                try:
                    self.sock.close()
                except:
                    pass  # Make sure it's closed before recreating the server

                self.sock = socket.create_server(('0.0.0.0', self.port))
                retries = SERVER_START_RETRIES
                while self.run_event.is_set():
                    conn, addr = self.sock.accept()  # blocking, don't need time sleep
                    conn.setblocking(False)
                    self.lock_connections.acquire()
                    connection = Connection(conn, self.password)
                    connection.register_listener(
                        'main', self._thread_listener, (self,))
                    self.connections.append(connection)
                    self.lock_connections.release()
                    if not self.run_event.is_set():
                        self.sock.close()
                        break
            except OSError as err:
                if retries <= 0:
                    return
                print(err, file=sys.stderr)
                retries -= 1

    def _thread_listener(self, obj, conn):
        if isinstance(obj, Command):
            self.lock_commands.acquire()
            self.execute(conn, obj)
            self.lock_commands.release()
        if isinstance(obj, Message):
            self.lock_messages.acquire()
            self.messages.append(obj)
            self.lock_commands.release()

    def execute(self, conn, command):
        """Executes a command and sends the result back to the remote brick (rem)"""
        pass
