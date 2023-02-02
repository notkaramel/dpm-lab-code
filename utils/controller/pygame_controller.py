import pygame
import threading
import time
import enum
import json


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
    SLEEP_INTERVAL = 0.5

    @classmethod
    def get_instance(cls):
        if cls.MANAGER is None:
            cls.MANAGER = GamepadManager()
        return cls.MANAGER

    def __init__(self):
        if self.MANAGER is not None:
            raise RuntimeError(
                "Cannot create a second instance of GamepadManager")

        self.gamepads = {}
        self.assigners = []
        self.lock_assigners = threading.Lock()
        self.profiles = {}

    def register(self, json_profile):
        data = json.loads(json_profile)
        self.profiles[data['name']] = data['keys']

    def init(self):
        pygame.init()
        self.thread = threading.Thread(target=self.process_events, daemon=True)
        self.thread.start()

    def add_assigner(self, assigner):
        self.lock_assigners.acquire()
        self.assigners.append(assigner)
        self.lock_assigners.release()

    def process_events(self):
        try:
            while True:
                # Handle adding and removing gamepads
                event = pygame.event.poll()
                if event.type == pygame.JOYDEVICEADDED:
                    index = event.device_index
                    joystick = pygame.joystick.Joystick(index)
                    g = _Gamepad(joystick)
                    self.gamepads[joystick.get_instance_id()] = g
                if event.type == pygame.JOYDEVICEREMOVED:
                    del self.gamepads[event.instance_id]

                for gamepad in self.gamepads.values():
                    print(gamepad.all())
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

    def __init__(self, joystick):
        self.joystick = joystick
        self.profile = {}
        profile = GamepadManager.get_instance().profiles.get(self.type(), None)

        if profile is not None:
            self.set_profile(profile)

    def set_profile(self, profile):
        for key, identifiers in profile.items():
            for identifier in identifiers:
                self.profile[Inputs[identifier]] = key

    def type(self):
        return self.joystick.get_name()

    def all(self):
        text = ""
        pygame.event.get()
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
        pygame.event.get()
        if type(key) != Inputs:
            key = Inputs.value(key)
        command: str = self.profile[key]  # B, A, H, L
        if 'B' in command:
            return self.joystick.get_button(int(command[1:]))
        if 'A' in command:
            if '.' in command:
                part = command[1:].split('.')
                index = int(part[0])
                direction = int(part[1])
                return self.joystick.get_axis(index) * ((-1)**(direction % 2)) < 0
            else:
                return self.joystick.get_axis(int(command[1:]))
        if 'H' in command:
            if '.' in command:
                part = command[1:].split('.')
                index = int(part[0])
                direction = int(part[1])
                axis = direction // 2
                return self.joystick.get_hat(index)[axis] * ((-1)**(direction % 2)) < 0
            else:
                return self.joystick.get_hat(int(command[1:]))
        if 'L' in command:
            return self.joystick.get_ball(int(command[1:]))

        return None


class Gamepad:
    """Define this as a gamepad that can be assigned by pressing a given key-combination"""

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
        if self.controller_type is not None and gamepad.type() != self.controller_type:
            return
        if all([gamepad.get(button) for button in self.button_combination]):
            print("succeeding")
            self.gamepad = gamepad

    def unassign(self):
        self.gamepad = None

    def get(self, key):
        if self.gamepad is None:
            return None
        return self.gamepad.get(key)


if __name__ == '__main__':
    GamepadManager.get_instance().init()
    gm = GamepadManager.get_instance()
