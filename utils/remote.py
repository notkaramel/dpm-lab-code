import brick
import socket
import pickle
import socketserver
import threading
import time
from .. import brickpi3

TIMEOUT = socket.getdefaulttimeout()
DEFAULT_PORT = 2110
THREAD_SLEEP = 0.100
BUSY_WAITING = 0.100


class Message:
    def __init__(self, text, password):
        self.text = text
        self.password = password


class Command:
    def __init__(self, func_name, password, *args, **kwargs):
        self.func_name = func_name
        self.password = password
        self.args = args
        self.kwargs = kwargs
        self.id = id(self)


class RemoteBrickServer(object):
    def __init__(self, port=None, password="password"):
        pass

class RemoteBrick(object):
    def __init__(self, address, password="password"):
        self.messages = []
        self.buffer = {}
        self.lock_message = threading.Lock()
        self.lock_buffer = threading.Lock()
        self.lock_sock = threading.Lock()
        self.run_event = threading.Event()
        self._status = None

        self.address = address
        self.password = password

        self._restart()

    def get_remote_status(self):
        return self._status, self.run_event.is_set()

    def _restart(self):
        self.run_event.clear()
        self.lock_sock.acquire()
        self.sock = socket.create_connection(
            (self.address, DEFAULT_PORT), TIMEOUT)
        self.run_event.set()

        self.lock_sock.release()
        self.thread = threading.Thread(
            target=RemoteBrick._thread_func, args=(self,), daemon=True)

    def _thread_func(self):
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
        self.lock_sock.acquire()
        self.sock.shutdown()
        self.sock.close()
        self.lock_sock.release()

    def _send(self, data, tries=5, err=None):
        if tries <= 0 and err is not None:
            raise err

        try:
            self.lock_sock.acquire()
            self.sock.send(data)
            self.lock_sock.release()
        except ConnectionResetError as err:
            self._restart()
            self._send(data, tries-1, err)

    def __del__(self):
        self.sock.close()

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


class Enumeration(object):
    def __init__(self, names):  # or *names, with no .split()
        number = 0
        for line, name in enumerate(names.split('\n')):
            if name.find(",") >= 0:
                # strip out the spaces
                while(name.find(" ") != -1):
                    name = name[:name.find(" ")] + name[(name.find(" ") + 1):]

                # strip out the commas
                while(name.find(",") != -1):
                    name = name[:name.find(",")] + name[(name.find(",") + 1):]

                # if the value was specified
                if(name.find("=") != -1):
                    number = int(float(name[(name.find("=") + 1):]))
                    name = name[:name.find("=")]

                # optionally print to confirm that it's working correctly
                # print "%40s has a value of %d" % (name, number)

                setattr(self, name, number)
                number = number + 1


class FirmwareVersionError(Exception):
    """Exception raised if the BrickPi3 firmware needs to be updated"""


class SensorError(Exception):
    """Exception raised if a sensor is not yet configured when trying to read it with get_sensor"""


class BrickPi3(brickpi3.BrickPi3):
    PORT_1 = 0x01
    PORT_2 = 0x02
    PORT_3 = 0x04
    PORT_4 = 0x08

    PORT_A = 0x01
    PORT_B = 0x02
    PORT_C = 0x04
    PORT_D = 0x08

    MOTOR_FLOAT = -128

    SensorType = [0, 0, 0, 0]
    I2CInBytes = [0, 0, 0, 0]

    I2C_LENGTH_LIMIT = 16

    BPSPI_MESSAGE_TYPE = Enumeration("""
        NONE,

        GET_MANUFACTURER,
        GET_NAME,
        GET_HARDWARE_VERSION,
        GET_FIRMWARE_VERSION,
        GET_ID,
        SET_LED,
        GET_VOLTAGE_3V3,
        GET_VOLTAGE_5V,
        GET_VOLTAGE_9V,
        GET_VOLTAGE_VCC,
        SET_ADDRESS,

        SET_SENSOR_TYPE,

        GET_SENSOR_1,
        GET_SENSOR_2,
        GET_SENSOR_3,
        GET_SENSOR_4,

        I2C_TRANSACT_1,
        I2C_TRANSACT_2,
        I2C_TRANSACT_3,
        I2C_TRANSACT_4,

        SET_MOTOR_POWER,

        SET_MOTOR_POSITION,

        SET_MOTOR_POSITION_KP,

        SET_MOTOR_POSITION_KD,

        SET_MOTOR_DPS,

        SET_MOTOR_DPS_KP,

        SET_MOTOR_DPS_KD,

        SET_MOTOR_LIMITS,

        OFFSET_MOTOR_ENCODER,

        GET_MOTOR_A_ENCODER,
        GET_MOTOR_B_ENCODER,
        GET_MOTOR_C_ENCODER,
        GET_MOTOR_D_ENCODER,

        GET_MOTOR_A_STATUS,
        GET_MOTOR_B_STATUS,
        GET_MOTOR_C_STATUS,
        GET_MOTOR_D_STATUS,
    """)

    SENSOR_TYPE = Enumeration("""
        NONE = 1,
        I2C,
        CUSTOM,

        TOUCH,
        NXT_TOUCH,
        EV3_TOUCH,

        NXT_LIGHT_ON,
        NXT_LIGHT_OFF,

        NXT_COLOR_RED,
        NXT_COLOR_GREEN,
        NXT_COLOR_BLUE,
        NXT_COLOR_FULL,
        NXT_COLOR_OFF,

        NXT_ULTRASONIC,

        EV3_GYRO_ABS,
        EV3_GYRO_DPS,
        EV3_GYRO_ABS_DPS,

        EV3_COLOR_REFLECTED,
        EV3_COLOR_AMBIENT,
        EV3_COLOR_COLOR,
        EV3_COLOR_RAW_REFLECTED,
        EV3_COLOR_COLOR_COMPONENTS,

        EV3_ULTRASONIC_CM,
        EV3_ULTRASONIC_INCHES,
        EV3_ULTRASONIC_LISTEN,

        EV3_INFRARED_PROXIMITY,
        EV3_INFRARED_SEEK,
        EV3_INFRARED_REMOTE,
    """)

    SENSOR_STATE = Enumeration("""
        VALID_DATA,
        NOT_CONFIGURED,
        CONFIGURING,
        NO_DATA,
        I2C_ERROR,
    """)

    SENSOR_CUSTOM = Enumeration("""
        PIN1_9V,
        PIN5_OUT,
        PIN5_STATE,
        PIN6_OUT,
        PIN6_STATE,
        PIN1_ADC,
        PIN6_ADC,
    """)
    """
    Flags for use with SENSOR_TYPE.CUSTOM

    PIN1_9V
        Enable 9V out on pin 1 (for LEGO NXT Ultrasonic sensor).

    PIN5_OUT
        Set pin 5 state to output. Pin 5 will be set to input if this flag is not set.

    PIN5_STATE
        If PIN5_OUT is set, this will set the state to output high, otherwise the state will
        be output low. If PIN5_OUT is not set, this flag has no effect.

    PIN6_OUT
        Set pin 6 state to output. Pin 6 will be set to input if this flag is not set.

    PIN6_STATE
        If PIN6_OUT is set, this will set the state to output high, otherwise the state will
        be output low. If PIN6_OUT is not set, this flag has no effect.

    PIN1_ADC
        Enable the analog/digital converter on pin 1 (e.g. for NXT analog sensors).

    PIN6_ADC
        Enable the analog/digital converter on pin 6.
    """

    SENSOR_CUSTOM.PIN1_9V = 0x0002
    SENSOR_CUSTOM.PIN5_OUT = 0x0010
    SENSOR_CUSTOM.PIN5_STATE = 0x0020
    SENSOR_CUSTOM.PIN6_OUT = 0x0100
    SENSOR_CUSTOM.PIN6_STATE = 0x0200
    SENSOR_CUSTOM.PIN1_ADC = 0x1000
    SENSOR_CUSTOM.PIN6_ADC = 0x4000

    SENSOR_I2C_SETTINGS = Enumeration("""
        MID_CLOCK,
        PIN1_9V,
        SAME,
        ALLOW_STRETCH_ACK,
        ALLOW_STRETCH_ANY,
    """)

    # Send the clock pulse between reading and writing. Required by the NXT US sensor.
    SENSOR_I2C_SETTINGS.MID_CLOCK = 0x01
    SENSOR_I2C_SETTINGS.PIN1_9V = 0x02  # 9v pullup on pin 1
    # Keep performing the same transaction e.g. keep polling a sensor
    SENSOR_I2C_SETTINGS.SAME = 0x04

    MOTOR_STATUS_FLAG = Enumeration("""
        LOW_VOLTAGE_FLOAT,
        OVERLOADED,
    """)

    # If the motors are floating due to low battery voltage
    MOTOR_STATUS_FLAG.LOW_VOLTAGE_FLOAT = 0x01
    # If the motors aren't close to the target (applies to position control and dps speed control).
    MOTOR_STATUS_FLAG.OVERLOADED = 0x02

    #SUCCESS = 0
    #SPI_ERROR = 1
    #SENSOR_ERROR = 2
    #SENSOR_TYPE_ERROR = 3

    def __init__(self, addr=1, detect=True):
        self.sender = None
        pass

    def spi_transfer_array(self, data_out):
        pass

    def spi_write_8(self, MessageType, Value):
        pass

    def spi_read_16(self, MessageType):
        pass

    def spi_write_16(self, MessageType, Value):
        pass

    def spi_write_24(self, MessageType, Value):
        pass

    def spi_read_32(self, MessageType):
        pass

    def spi_write_32(self, MessageType, Value):
        pass

    def get_manufacturer(self):
        pass

    def get_board(self):
        pass

    def get_version_hardware(self):
        pass

    def get_version_firmware(self):
        pass

    def get_id(self):
        pass

    def set_led(self, value):
        pass

    def get_voltage_3v3(self):
        pass

    def get_voltage_5v(self):
        pass

    def get_voltage_9v(self):
        pass

    def get_voltage_battery(self):
        pass

    def set_sensor_type(self, port, type, params=0):
        pass

    def transact_i2c(self, port, Address, OutArray, InBytes):
        pass

    def get_sensor(self, port):
        pass

    def set_motor_power(self, port, power):
        pass

    def set_motor_position(self, port, position):
        pass

    def set_motor_position_relative(self, port, degrees):
        pass

    def set_motor_position_kp(self, port, kp=25):
        pass

    def set_motor_position_kd(self, port, kd=70):
        pass

    def set_motor_dps(self, port, dps):
        pass

    def set_motor_limits(self, port, power=0, dps=0):
        pass

    def get_motor_status(self, port):
        pass

    def get_motor_encoder(self, port):
        pass

    def offset_motor_encoder(self, port, position):
        pass

    def reset_motor_encoder(self, port):
        pass

    def reset_all(self):
        pass
