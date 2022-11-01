from utils import brick, telemetry
from collections import Counter
import time
import math
import threading

# 0 is starting pos. use 90dps.
POSITIONS = [-70, -160, -255, -360, -450, -545]
RESET_DISTANCE = 600


COLORS = {  # means, stdevs, threshold on stdev distance
    'red': ((0.9720, 0.1305, 0.1947), (0.003706, 0.01108, 0.01371), 3),
    'blue': ((0.1782, 0.3947, 0.9006), (0.02419, 0.02570, 0.01359), 3),
    'green': ((0.1633, 0.8940, 0.4161), (0.02180, 0.009301, 0.02003), 3),
    'purple': ((0.4383, 0.3476, 0.8280), (0.02114, 0.02571, 0.01800), 3),
    'yellow': ((0.7897, 0.6028, 0.1118), (0.01153, 0.01698, 0.01152), 3),
    'orange': ((0.9284, 0.2587, 0.2658), (0.005521, 0.01204, 0.01703), 3)
}


def vector_length(a, b, c):
    """Gives length of vector"""
    return math.sqrt(a*a + b*b + c*c)


def normalize(r, g, b):
    """Normalizes a vector"""
    if r is None or g is None or b is None:
        return 0, 0, 0

    n = math.sqrt(r*r + g*g + b*b)
    n = 1/n if n != 0 else 0
    return r*n, g*n, b*n


def color_dist(rgb):
    """Returns a color string of the closest color using standard deviation-scaled distance.

    The given rgb value, treated as a vector, is converted to stdev_distance by the formula:
        stdev_components = abs(rgb-mean)/stdev
        stdev_distance = sqrt(stdev_components**2)

    What this does is convert every rgb component value into direct distance to 
    the mean rgb components of the previously collected color data, then converts 
    these units into "number of standard deviations from r, g, and b means". Now 
    that the units are in standard deviations, we treat this as a vector too, and 
    get its length. With this stdev_distance, we can rely on statistics to tell 
    us that if it is under the value 3, the original point, rgb, is completely 
    within the curves of the collected color.

    If the stdev_distance to all colors is farther than 3, then we can assume 
    that this rgb value is not within any of the existing learned colors.

    (This value of 3 is treated as a max threshold, and can be adjusted for each 
    color individually)

    """
    color_order = []
    distances = []
    rgb = normalize(*rgb)
    for color, (mean, std, threshold) in COLORS.items():
        r, g, b = [abs(c-m)/s for c, m, s in zip(rgb, mean, std)]
        d = vector_length(r, g, b)
        if d <= threshold:
            distances.append(d)
            color_order.append(color)

    if len(distances) == 0:
        return "unknown"
    i = distances.index(min(distances))
    return color_order[i]


def window_start():
    telemetry.start()
    telemetry.resize(500, 500)

    telemetry.label("STATUS", "Initializing", True)

    sort_button = telemetry.create_button("Start Sorting")
    color_buttons = {
        color: telemetry.create_button(f"Retrieve {color}") for color in COLORS.keys()
    }
    return sort_button, color_buttons


def block_position_relative(motor: brick.Motor, degrees, dps=90, threshold=2):
    motor.set_limits(dps=dps)
    end = motor.get_position() + degrees
    motor.set_position_relative(degrees)
    time.sleep(0.1)

    # Keep waiting until we are at the position and stopped
    while abs(end - motor.get_position()) > threshold or motor.get_speed() > 1:
        time.sleep(0.1)
    motor.set_power(0)
    time.sleep(0.5)


def block_position(motor: brick.Motor, degrees, dps=90, threshold=2):
    motor.set_limits(dps=dps)

    motor.set_position(degrees)
    time.sleep(0.1)

    # Keep waiting until we are at the position and stopped
    while abs(motor.get_position() - degrees) > threshold or motor.get_speed() > 1:
        time.sleep(0.1)
    motor.set_power(0)
    time.sleep(0.5)


def determine_color(color_sensor: brick.EV3ColorSensor, window=10):
    counter = Counter()
    while True:
        sample_set = []
        for i in range(window):
            sample_set.append(color_dist(color_sensor.get_rgb()))
            time.sleep(0.01)
        counter.update(sample_set)
        if len(counter) == 1 or counter.most_common()[0][1] > counter.most_common()[1][1]:
            return counter.most_common()[0][0]


def sort_cubes(sorting_list, selector: brick.Motor, color_sensor: brick.EV3ColorSensor):
    def inner():
        for i, position in enumerate(POSITIONS):
            block_position(selector, position)
            color = determine_color(color_sensor)
            sorting_list.append(color)

    thread = threading.Thread(target=inner, daemon=True)

    thread.start()
    return thread


def retrieve_cube(index: int, selector: brick.Motor, pusher: brick.Motor):
    def inner():
        block_position(selector, POSITIONS[index])
        block_position_relative(pusher, -360)
    thread = threading.Thread(target=inner, daemon=True)
    # thread.is_alive()
    thread.start()
    return thread


if __name__ == '__main__':
    sort_button, color_buttons = window_start()

    color_sensor = brick.EV3ColorSensor(3)
    pusher = brick.Motor('D')
    selector = brick.Motor('C')

    if hasattr(brick.BP, "set_sensor"):
        # Then we are using the dummy test brick
        brick.BP.set_sensor(0x04, (0.9720, 0.1305, 0.1947, 0))

    try:
        pusher.set_dps(0)  # Should be phyiscally in the correct position

        selector.set_limits(dps=90)
        pusher.set_limits(dps=90)
        # Reset to starting position
        block_position_relative(selector, RESET_DISTANCE, threshold=20)
        selector.reset_encoder()  # Set this position to be the 0th position

        MODE = None
        SORTING_LIST = []
        MAX_CUBES = len(POSITIONS)
        REQUESTED_COLOR = None  # index in the SORTING_LIST
        REQUESTED_COLOR_NAME = None
        current_thread = None  # The current action being executed
        # brick.wait_ready_sensors(True)
        telemetry.label("STATUS", "Sorter is Ready", True)
        while True:
            if not telemetry.isopen():
                break

            # MODE is stuck on None, until we press the sort_button
            if sort_button.is_pressed() and MODE is None:
                telemetry.label("STATUS", "Sort Initiated", True)
                MODE = "Sorting"

            # MODE will be stuck on Sorting, until the SORTING_LIST is full
            if MODE == "Sorting":
                # Do the sort action once
                if current_thread is None:
                    telemetry.label("STATUS", "Sort Active", True)
                    current_thread = sort_cubes(
                        SORTING_LIST, selector, color_sensor)
                if not current_thread.is_alive() and len(SORTING_LIST) == MAX_CUBES:
                    telemetry.label("STATUS", f"Sort Finished: {SORTING_LIST}", True)
                    MODE = "Retrieving"
                    current_thread = None
                elif len(SORTING_LIST) > MAX_CUBES:
                    # ERROR: Somehow got more colors than we should have!
                    raise Exception(
                        f"Cannot find more colors than we can store. Expected {MAX_CUBES} got {len(SORTING_LIST)}")

            if MODE == "Retrieving":

                # Sets REQUESTED_COLOR
                for color, button in color_buttons.items():
                    if button.is_pressed():
                        if color in SORTING_LIST and REQUESTED_COLOR is None:
                            REQUESTED_COLOR_NAME = color
                            REQUESTED_COLOR = SORTING_LIST.index(
                                color)  # We retrieve this color
                            SORTING_LIST[REQUESTED_COLOR] = None
                            telemetry.label("STATUS", f"Chosen {color}", True)
                        elif color not in SORTING_LIST:
                            telemetry.label("STATUS", f"{color} is not available on the robot", True)
                            pass  # WARNING: color not available in robot
                        elif REQUESTED_COLOR is not None:
                            telemetry.label("STATUS", f"Cube #{REQUESTED_COLOR}: {REQUESTED_COLOR_NAME} is currently being retrieved", True)
                            pass  # WARNING: color currently being retrieved
                        # A slight pause, to press button only once
                        time.sleep(0.5)

                # Uses REQUESTED_COLOR
                if REQUESTED_COLOR is not None and current_thread is None:
                    # Start retrieval
                    telemetry.label("STATUS", f"Retrieving Cube #{REQUESTED_COLOR}: {REQUESTED_COLOR_NAME}", True)
                    current_thread = retrieve_cube(
                        REQUESTED_COLOR, selector, pusher)
                if REQUESTED_COLOR is not None and not current_thread.is_alive():
                    # Retrieval has completed
                    telemetry.label("STATUS", f"Finished retrieving {REQUESTED_COLOR_NAME} | {SORTING_LIST}", True)
                    REQUESTED_COLOR = None
                    current_thread = None
            telemetry.label("Stored Colors", f"{SORTING_LIST}", True)
            telemetry.update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        exit(0)
