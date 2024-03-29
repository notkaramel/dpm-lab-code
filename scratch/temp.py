

from statistics import mean, stdev
from utils import brick, telemetry
from collections import Counter, defaultdict
import time
import math

BASE_SPEED = 180
MAX_SPEED = 720
P_CONSTANT = 300.0
I_CONSTANT = 200.0

COLOR_MARKERS = (
    ('blue_tape', 13),
    ('gray_table', 13),
    ('red_tape', 13),
    ('gray_table', 13),
)

COLOR_DATA = "temp_calibration.csv"

COLORS = {  # means, stdevs, threshold on stdev distance
    'red': ((0.9720, 0.1305, 0.1947), (0.003706, 0.01108, 0.01371), 7.5),
    'blue': ((0.1782, 0.3947, 0.9006), (0.02419, 0.02570, 0.01359), 7.5),
    'green': ((0.1633, 0.8940, 0.4161), (0.02180, 0.009301, 0.02003), 10),
    'purple': ((0.4383, 0.3476, 0.8280), (0.02114, 0.02571, 0.01800), 7.5),
    'yellow': ((0.7897, 0.6028, 0.1118), (0.01153, 0.01698, 0.01152), 7.5),
    'orange': ((0.9284, 0.2587, 0.2658), (0.005521, 0.01204, 0.01703), 7.5)
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

        distances.append(d)
        color_order.append(color)

    if len(distances) == 0:
        return "unknown", 0
    d = min(distances)
    if d > threshold:
        return "unknown", round(d, 2)
    i = distances.index(d)
    return color_order[i], round(d, 2)


def collect_stats(filename, markers):
    """
    markers : list of (key, threshold)

    Returns format:

    {
        marker : (r_mean, g_mean, b_mean), (r_std, g_std, b_std)
    }
    """
    data = None
    with open(filename, 'r') as f:
        data = [list(map(int, line.strip().split(',')))
                for line in f.readlines() if line.strip()]
        data = [list(normalize(*sample[0:3]))+[sample[3]] for sample in data]
    collected_data = defaultdict(list)
    reverse_keys = {}
    for i, (marker, threshold) in enumerate(markers):
        reverse_keys[i] = (marker, threshold)
    for dat in data:
        r, g, b, i = dat
        key, _ = reverse_keys[dat[3]]
        collected_data[key].append(dat[0:3])

    result = {}
    for key, rows in collected_data.items():
        r, g, b = zip(*rows)
        threshold = dict(markers)[key]
        result[key] = (
            (mean(r), mean(g), mean(b)),
            (stdev(r), stdev(g), stdev(b)),
            threshold
        )
    print(result)
    return result


# Loading color training data...
COLORS = collect_stats(COLOR_DATA, COLOR_MARKERS)


def window_start():
    telemetry.start()
    telemetry.resize(500, 500)

    telemetry.label("STATUS", "Initializing", True)

    # P Constant controls
    telemetry.label("P Constant", P_CONSTANT, True)

    def update_p_constant(slider: telemetry._Slider):
        global P_CONSTANT
        P_CONSTANT = slider.get_value()
        telemetry.label("P Constant", P_CONSTANT, True)
    telemetry.create_slider(0, MAX_SPEED, P_CONSTANT, update_p_constant)

    # I Constant controls
    telemetry.label("I Constant", I_CONSTANT, True)

    def update_i_constant(slider: telemetry._Slider):
        global I_CONSTANT
        I_CONSTANT = slider.get_value()
        telemetry.label("I Constant", I_CONSTANT, True)
    telemetry.create_slider(0, MAX_SPEED, I_CONSTANT, update_i_constant)

    telemetry.update()


def determine_color(color_sensor: brick.EV3ColorSensor, window=10):
    counter = Counter()
    while True:
        sample_set = []
        sample_dists = defaultdict(list)
        for i in range(window):
            detected, dist = color_dist(color_sensor.get_rgb())
            sample_dists[detected].append(dist)
            sample_set.append(detected)
            time.sleep(0.01)
        counter.update(sample_set)
        if len(counter) == 1 or counter.most_common()[0][1] > counter.most_common()[1][1]:
            return counter.most_common()[0][0], counter.most_common(), sample_dists


class ObjectFunction:
    def __init__(self, func):
        self._func = func

    def __call__(self, *args, **kwargs):
        return self._func(self, *args, **kwargs)


@ObjectFunction
def controller_PI_1(self, final_color):
    if final_color == 'gray_table' or final_color == 'unknown':
        # Forward
        self.motor_left.set_dps(BASE_SPEED)
        self.motor_right.set_dps(BASE_SPEED)
        self.detection_start_time = None
    else:
        if self.detection_start_time is None:
            self.detection_start_time = time.time()
        self.delta = P_CONSTANT + I_CONSTANT * \
            (time.time() - self.detection_start_time)
        self.delta = min(self.delta, MAX_SPEED)

    if final_color == 'red_tape':
        # Right
        self.motor_right.set_dps(BASE_SPEED + self.delta)
        self.motor_left.set_dps(BASE_SPEED)
    elif final_color == 'blue_tape':
        # Left
        self.motor_right.set_dps(BASE_SPEED)
        self.motor_left.set_dps(BASE_SPEED + self.delta)


@ObjectFunction
def controller_bang_bang(self, final_color):
    if final_color == 'gray_table':
        self.motor_left.set_dps(self.BASE_SPEED)
        self.motor_right.set_dps(self.BASE_SPEED)
    if final_color == 'red_tape':
        self.motor_left.set_dps(self.BASE_SPEED - self.DELTA)
        self.motor_right.set_dps(self.BASE_SPEED)
    if final_color == 'blue_tape':
        self.motor_left.set_dps(self.BASE_SPEED)
        self.motor_right.set_dps(-self.BASE_SPEED - self.DELTA)


@ObjectFunction
def controller_slowest(self, final_color):
    if final_color == 'gray_table':
        self.motor_left.set_dps(self.BASE_SPEED)
        self.motor_right.set_dps(self.BASE_SPEED)
    if final_color == 'red_tape':
        self.motor_left.set_dps(-self.BASE_SPEED)
        self.motor_right.set_dps(self.BASE_SPEED)
    if final_color == 'blue_tape':
        self.motor_left.set_dps(self.BASE_SPEED)
        self.motor_right.set_dps(-self.BASE_SPEED)


def main():
    motor_left = brick.Motor('D')
    motor_right = brick.Motor('A')
    touch_sensor = brick.TouchSensor(1)
    color_sensor = brick.EV3ColorSensor(3)

    sensor_left = brick.TouchSensor(2)
    sensor_right = brick.TouchSensor(4)
    window_start()
    brick.wait_ready_sensors(True)

    motor_left.set_dps(0)
    motor_right.set_dps(0)
    motor_left.reset_encoder()
    motor_right.reset_encoder()

    controller_PI_1.detection_start_time = None
    controller_PI_1.delta = 0
    controller_PI_1.motor_left, controller_PI_1.motor_right = motor_left, motor_right

    controller_bang_bang.motor_left, controller_bang_bang.motor_right = motor_left, motor_right
    controller_bang_bang.BASE_SPEED = 200
    controller_bang_bang.DELTA = 100

    controller_slowest.motor_left, controller_slowest.motor_right = motor_left, motor_right
    controller_slowest.BASE_SPEED = 200

    counter = 0
    while True:
        time.sleep(0.01)
        if touch_sensor.is_pressed():
            break

        # sample = color_sensor.get_rgb()
        final_color, potentials, color_distances = determine_color(
            color_sensor, window=5)

        controller_PI_1(final_color)

        telemetry.label("Current Color", final_color, True)
        telemetry.label("Detected Colors", potentials, True)
        if counter % 10 == 0:
            telemetry.label("Sample Colors", '\n'.join(list(map(str, color_distances.items()))), True)

        telemetry.update()
        counter += 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
