import pygame
import threading
import time
import enum
import json
import re


class Inputs(enum.Enum):
    DPAD_UP = enum.auto()
    DPAD_DOWN = enum.auto()
    DPAD_LEFT = enum.auto()
    DPAD_RIGHT = enum.auto()
    A = enum.auto()
    B = enum.auto()
    X = enum.auto()
    Y = enum.auto()
    CIRCLE = enum.auto()
    CROSS = enum.auto()
    SQUARE = enum.auto()
    TRIANGLE = enum.auto()
    L_BUMPER = enum.auto()
    R_BUMPER = enum.auto()
    L_TRIGGER = enum.auto()
    R_TRIGGER = enum.auto()
    SL = enum.auto()
    SR = enum.auto()
    L = enum.auto()
    R = enum.auto()
    ZL = enum.auto()
    ZR = enum.auto()
    BACK = enum.auto()
    START = enum.auto()
    GUIDE = enum.auto()
    SHARE = enum.auto()
    PS = enum.auto()
    OPTIONS = enum.auto()
    L_STICK = enum.auto()
    R_STICK = enum.auto()
    CAPTURE = enum.auto()
    HOME = enum.auto()
    PLUS = enum.auto()
    MINUS = enum.auto()
    TOUCH_PAD_CLICK = enum.auto()
    LEFT_STICK_X = enum.auto()
    LEFT_STICK_Y = enum.auto()
    RIGHT_STICK_X = enum.auto()
    RIGHT_STICK_Y = enum.auto()

    @staticmethod
    def value(key):
        if type(key) == int:
            return Inputs(key)
        if type(key) == str:
            return Inputs[key.upper()]


class InputGroups():
    pass


"""Wireless Gamepad Left
D-pad Up        - Button 0
D-pad Down      - Button 1
D-pad Left      - Button 2
D-pad Right     - Button 3
SL              - Button 4
SR              - Button 5
-               - Button 8
Stick In        - Button 10
Capture         - Button 13
L               - Button 14
ZL              - Button 15

Down -> Up      - Y Axis
Left -> Right   - X Axis
"""

"""Wireless Gamepad Right
A Button        - Button 0
B Button        - Button 1
X Button        - Button 2
Y Button        - Button 3
SL              - Button 4
SR              - Button 5
+               - Button 9
Stick In        - Button 11
Home            - Button 12
R               - Button 14
ZR              - Button 15

Down -> Up      - Y Axis
Left -> Right   - X Axis
"""

"""Nintendo Switch Pro Controller
Left:
Left -> Right   - Axis 0
Up -> Down      - Axis 1

Right:
Left -> Right   - Axis 2
Up -> Down      - Axis 3

Left Trigger:
Out -> In       - Axis 4

Right Trigger:
Out -> In       - Axis 5

A Button        - Button 0
B Button        - Button 1
X Button        - Button 2
Y Button        - Button 3
- Button        - Button 4
Home Button     - Button 5
+ Button        - Button 6
L. Stick In     - Button 7
R. Stick In     - Button 8
Left Bumper     - Button 9
Right Bumper    - Button 10
D-pad Up        - Button 11
D-pad Down      - Button 12
D-pad Left      - Button 13
D-pad Right     - Button 14
Capture Button  - Button 15
"""


class GamepadManager:
    MANAGER = None
    SLEEP_INTERVAL = 0.01

    @classmethod
    def get_instance(cls):
        if cls.MANAGER is None:
            cls.MANAGER = GamepadManager()
        return cls.MANAGER

    def __init__(self):
        if self.MANAGER is not None:
            raise RuntimeError(
                "Cannot create a second instance of GamepadManager")

        self._gamepads = {}
        self.assigners = []
        self.lock_assigners = threading.Lock()
        self.profiles = {}

    @classmethod
    def register(cls, json_profile):
        data = json.loads(json_profile)
        cls.get_instance().profiles[data['name']] = data['keys']

    @classmethod
    def init(cls):
        self = cls.get_instance()
        pygame.init()
        self.thread = threading.Thread(target=self.process_events, daemon=True)
        self.thread.start()

    @staticmethod
    def update():
        pygame.event.pump()

    @classmethod
    def add_assigner(cls, assigner):
        self = cls.get_instance()
        self.lock_assigners.acquire()
        self.assigners.append(assigner)
        self.lock_assigners.release()

    @property
    def gamepads(self):
        return self._gamepads

    def process_events(self):
        try:
            while True:
                # Handle adding and removing gamepads
                try:
                    event = pygame.event.poll()
                except:
                    event = None
                if event is None:
                    pass
                elif event.type == pygame.JOYDEVICEADDED:
                    index = event.device_index
                    joystick = pygame.joystick.Joystick(index)
                    g = _Gamepad(joystick)
                    self._gamepads[joystick.get_instance_id()] = g
                elif event.type == pygame.JOYDEVICEREMOVED:
                    del self._gamepads[event.instance_id]

                for gamepad in self._gamepads.values():
                    self.lock_assigners.acquire()
                    for assigner in self.assigners:
                        assigner._attempt(gamepad)
                    self.lock_assigners.release()

                time.sleep(self.SLEEP_INTERVAL)

        except Exception as e:
            print(e)


GamepadManager.get_instance().register('''{
    "name": "Xbox 360 Controller",
    "keys": {
        "A0" : ["LEFT_STICK_X"],
        "A1" : ["LEFT_STICK_Y"],
        "A3" : ["RIGHT_STICK_X"],
        "A4" : ["RIGHT_STICK_Y"],
        "A2" : ["L_TRIGGER"],
        "A5" : ["R_TRIGGER"],
        "B0" : ["A"],
        "B1" : ["B"],
        "B2" : ["X"],
        "B3" : ["Y"],
        "B4" : ["L_BUMPER"],
        "B5" : ["R_BUMPER"],
        "B6" : ["BACK"],
        "B7" : ["START"],
        "B8" : ["L_STICK"],
        "B9" : ["R_STICK"],
        "B10" : ["GUIDE"],
        "H0.2" : ["DPAD_DOWN"],
        "H0.3" : ["DPAD_UP"],
        "H0.0" : ["DPAD_LEFT"],
        "H0.1" : ["DPAD_RIGHT"]
    }
}
''')

GamepadManager.get_instance().register("""{
    "name":"Controller (Xbox One For Windows)",
    "keys": {
        "A0" : ["LEFT_STICK_X"],
        "A1" : ["LEFT_STICK_Y"],
        "A2" : ["RIGHT_STICK_X"],
        "A3" : ["RIGHT_STICK_Y"],
        "A4" : ["L_TRIGGER"],
        "A5" : ["R_TRIGGER"],
        "B0" : ["A"],
        "B1" : ["B"],
        "B2" : ["X"],
        "B3" : ["Y"],
        "B4" : ["L_BUMPER"],
        "B5" : ["R_BUMPER"],
        "B6" : ["BACK"],
        "B7" : ["START"],
        "B8" : ["L_STICK"],
        "B9" : ["R_STICK"],
        "B10" : ["GUIDE"],
        "H0.2" : ["DPAD_DOWN"],
        "H0.3" : ["DPAD_UP"],
        "H0.0" : ["DPAD_LEFT"],
        "H0.1" : ["DPAD_RIGHT"]
    }
}
""")

GamepadManager.get_instance().register("""{
    "name":"Controller (XBOX 360 For Windows)",
    "keys": {
    "B0" : ["A"],
    "B1" : ["B"],
    "B2" : ["X"],
    "B3" : ["Y"],
    "B4" : ["L_BUMPER"],
    "B5" : ["R_BUMPER"],
    "B6" : ["BACK"],
    "B7" : ["START"],
    "B8" : ["L_STICK"],
    "B9" : ["R_STICK"],
    "H0.2" : ["DPAD_DOWN"],
    "H0.3" : ["DPAD_UP"],
    "H0.0" : ["DPAD_LEFT"],
    "H0.1" : ["DPAD_RIGHT"],
    "A0" : ["LEFT_STICK_X"],
    "A1" : ["LEFT_STICK_Y"],
    "A4" : ["RIGHT_STICK_X"],
    "A3" : ["RIGHT_STICK_Y"],
    "A2.0" : ["L_TRIGGER"],
    "A2.1" : ["R_TRIGGER"]
    }
}
""")


class _Gamepad:
    """Underlying unassigned gamepads"""
    RAW_INPUT_PATTERN = r'[A-Z][0-9]+(?:.[0-9]+)?'

    @staticmethod
    def update():
        """Updates the current state of all gamepads to the current output"""
        GamepadManager.update()

    def __init__(self, joystick):
        """This _Gamepad must be initialized using a valid Pygame joystick as input."""
        self.joystick = joystick
        self.profile = {}
        profile = GamepadManager.get_instance().profiles.get(self.gamepad_type(), None)

        if profile is not None:
            self.set_profile(profile)

    def set_profile(self, profile):
        """Sets the profile of this gamepad given a dictionary of mappings between 
        Inputs Enum keys and Pygame joystick input identifiers (i.e. B0, A1, H1.5, H1.3)
        """
        for key, identifiers in profile.items():
            for identifier in identifiers:
                self.profile[Inputs[identifier]] = key

    def gamepad_type(self):
        """Gets the joystick type of this gamepad."""
        return self.joystick.get_name()

    def raw_values(self):
        pygame.event.pump()
        B = []
        H = []
        A = []
        L = []
        for i in range(self.joystick.get_numbuttons()):
            B.append(self.joystick.get_button(i))
        for i in range(self.joystick.get_numhats()):
            H.append(self.joystick.get_hat(i))
        for i in range(self.joystick.get_numaxes()):
            A.append(self.joystick.get_axis(i))
        for i in range(self.joystick.get_numballs()):
            L.append(self.joystick.get_ball(i))

        return {'B': B, 'H': H, 'A': A, 'L': L}

    def __repr__(self):
        """Prints all raw Pygame input values."""
        text = ""
        pygame.event.pump()
        for i in range(self.joystick.get_numbuttons()):
            text += f"B{i}: {self.joystick.get_button(i)}\n"
        for i in range(self.joystick.get_numhats()):
            text += f"H{i}: {self.joystick.get_hat(i)}\n"
        for i in range(self.joystick.get_numaxes()):
            text += f"A{i}: {self.joystick.get_axis(i)}\n"
        for i in range(self.joystick.get_numballs()):
            text += f"L{i}: {self.joystick.get_ball(i)}\n"

        return text.strip()

    def get(self, key):
        """A universal get function that you should use.
        It accepts either Pygame input identifiers (see _Gamepad.get_raw)
        or Inputs Enum keys/names/indexes.

        Valid inputs include:

        "B0" for Button 0 (Not sure which button this will be)
        "A" for the A button on an XBOX controller or Nintendo Switch controller
        3 for the 4th Inupts Enum key, DPAD_RIGHT
        Inputs.LEFT_STICK_X to get the x axis (-1 to +1) of the left analog stick
        """
        pygame.event.pump()

        if re.fullmatch(_Gamepad.RAW_INPUT_PATTERN, key) is not None:
            return self.get_raw(key)
        if type(key) != Inputs:
            key = Inputs.value(key)
        command: str = self.profile[key]  # B, A, H, L
        return self.get_raw(command)

    def get_raw(self, key):
        """Retrieves the input value from the underlying Pygame joystick.
        It also uses a special syntax that lets us split Axes and Hats into
        component values:

        B - Button
        A - Axis
        H - Hat
        L - Ball

        B0 gets Button 0
        A1 gets Axis 1

        A1.0 gets -Axis 1
        A1.1 gets +Axis 1

        H1.0 gets -Axis X
        H1.1 gets +Axis X
        H1.2 gets -Axis Y
        H1.3 gets +Axis Y
        H1.4 gets Axis X of the hat as normal Axis
        H1.5 gets Axis Y of the hat as normal Axis
        """
        if 'B' == key[0]:
            return self.joystick.get_button(int(key[1:]))
        if 'A' == key[0]:
            if '.' in key:
                part = key[1:].split('.')
                index = int(part[0])
                direction = -1 if int(part[1]) == 0 else +1
                return max(self.joystick.get_axis(index) * direction, 0)
            else:
                return self.joystick.get_axis(int(key[1:]))
        if 'H' == key[0]:
            if '.' in key:
                part = key[1:].split('.')
                index = int(part[0])
                if part[1] == '4' or part[1] == '5':
                    return self.joystick.get_hat(index)[int(part[1]) - 4]
                direction = -1 if int(part[1]) % 2 == 0 else +1
                axis = direction // 2
                return max(self.joystick.get_hat(index)[axis] * direction, 0)
            else:
                return self.joystick.get_hat(int(key[1:]))
        if 'L' == key[0]:
            return self.joystick.get_ball(int(key[1:]))


class Gamepad:
    """Define this as a gamepad that can be assigned by pressing a given key-combination"""

    @staticmethod
    def update():
        GamepadManager.update()

    def __init__(self, button_combination, controller_type=None):
        """Create a gamepad that is assigned by the given button_combination

        if type is None, then it accepts any type of game controller
        if type is specified, it will only assign to game controllers of that type
        """

        self.button_combination = button_combination
        self.controller_type = controller_type
        self.gamepad = None
        GamepadManager.get_instance().add_assigner(self)

    def _attempt(self, gamepad: _Gamepad):
        if self.controller_type is not None and gamepad.gamepad_type() != self.controller_type:
            return
        if all([gamepad.get(button) for button in self.button_combination]):
            self.gamepad = gamepad

    def unassign(self):
        """Disables this Assigned Gamepad by detaching the physical gamepad from this object.

        Utilizing the assigning key combination again, will reassign that physical gamepad.
        """
        self.gamepad = None

    def get(self, key):
        """Get the value of a button, given a key.

        --Accepts multiple types of keys--

        Inputs Enum Keys
            Inputs.LEFT_STICK_X will get the left analog stick x axis
        Inputs Enum Key Names
            "L_BUMPER" will get the left click button on most controllers
        Inputs Enum Key Indexes
            3 will get the fourth Enum Key, DPAD_RIGHT


        --Special Joystick Identifiers--

        "B0" gets Button 0
        "H1" gets (x, y) of the second Hat
        "A2" gets the 3rd axis of a controller. -1 to +1. -1 is usually left and up 
            on analog axis sticks
        "A0.0" turns -1 to 0 to 1 on an axis to 1 to 0 to 0. So, if 
            Axis 0 is the Left Stick X axis, then A0.0 will be 1 if the stick is pushed left,
            0 if in the center, and 0 if towards the right.
        "A0.1" turns -1, 0, 1 on an axis into 0, 0, 1. So, if
            Axis 0 is the Left Stick X axis, then A0.1 will be 0 if the stick is left or center,
            and fully +1 when pushed to the right.
        "H0.0" and "H0.1" apply the axis splitting to the X component of the Hat.
        "H0.2" and "H0.3" apply the axis splitting to the Y component of the Hat.
        "H0.4" gives the X axis of the Hat like a normal Axis
        "H0.5" gives the Y axis of the Hat like a normal Axis

        """
        if self.gamepad is None:
            return None
        return self.gamepad.get(key)

    def __repr__(self):
        return f"Gamepad[combo({self.button_combination}), assigned:{self.gamepad.joystick.get_instance_id() if self.gamepad is not None else 'none'}]"

    def raw_values(self):
        """Gets all inputs from the gamepad if it exists.
        Does not give proper labels/names to each input.
        """
        return None if self.gamepad is None else self.gamepad.raw_values()


if __name__ == '__main__':
    import telemetry
    GamepadManager.get_instance().init()
    gm = GamepadManager.get_instance()
    gamepad = Gamepad(['B0', 'B1'])
    GamepadManager.update()

    def update():
        telemetry.label('output', gm.gamepads)
    telemetry.start_threaded(update)
