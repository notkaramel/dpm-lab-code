from . import brick
from . import dummy
from .rmi import RemoteClient, RemoteServer, isrelatedclass


class RemoteBrick(RemoteClient):
    def __init__(self, address, password, port=None, sock=None):
        super(RemoteBrick, self).__init__(address, password, port, sock)
        self._brick: dummy.Brick = self.create_caller(
            dummy.Brick(), var_name='brick')

    def get_brick(self):
        return self._brick

    def make_remote(self, sensor_or_motor, *args, **kwargs):
        """Creates a remote sensor or motor that is attached to the remote brick.
        sensor_or_motor - A class, such as Motor or EV3UltrasonicSensor
        *args - any of the normal arguments that would be used to create the object locally

        Returns None if you gave the wrong class.
        """
        if isrelatedclass(sensor_or_motor, (brick.Motor, brick.Sensor)):
            kwargs.update({'bp': self._brick})
            return sensor_or_motor(*args, **kwargs)
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


class RemoteBrickServer(RemoteServer):
    def __init__(self, password, port=None):
        super(RemoteBrickServer, self).__init__(password, port)
        self.register_object(brick.BP, var_name='brick')
