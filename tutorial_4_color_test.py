from numpy import minimum
from utils import brick, telemetry
import statistics as stats
import time
import math

SLIDER = [0, 720, 90]  # min, max, value

MOTOR_SPEED = 0
LAST_SPEED = 0
MOTOR_POS = 0

IS_SPEED_MODE = True

# 0 is starting pos. use 90dps.
POSITIONS = [-70, -160, -255, -360, -450, -545]
RESET_DISTANCE = 600


COLORS = { # means, stdevs, threshold on stdev distance
    'red': ((0.9720, 0.1305, 0.1947), (0.003706, 0.01108, 0.01371), 3),
    'blue': ((0.1782, 0.3947, 0.9006), (0.02419, 0.02570, 0.01359), 3),
    'green': ((0.1633, 0.8940, 0.4161), (0.02180, 0.009301, 0.02003), 3),
    'purple': ((0.4383, 0.3476, 0.8280), (0.02114, 0.02571, 0.01800), 3),
    'yellow': ((0.7897, 0.6028, 0.1118), (0.01153, 0.01698, 0.01152), 3),
    'orange': ((0.9284, 0.2587, 0.2658), (0.005521, 0.01204, 0.01703), 3)
}


def dist(a, b, c):
    return math.sqrt(a*a + b*b + c*c)


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
        d = dist(r, g, b)
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

    telemetry.label("SLIDER_VAL", SLIDER[2], True)
    telemetry.label("MOTOR_SPEED", MOTOR_SPEED, True)
    telemetry.label("MOTOR_POS", MOTOR_POS, True)
    telemetry.label("Motor Mode", "speed" if IS_SPEED_MODE else "pos", True)

    def update_slider(slider: telemetry._Slider, *args):
        SLIDER[2] = telemetry.remote(slider.get_value)
        telemetry.label("SLIDER_VAL", SLIDER[2], True)

    def update_speed_mode(button: telemetry._Button, *args):
        global IS_SPEED_MODE
        if button.is_pressed():
            IS_SPEED_MODE = not IS_SPEED_MODE
            telemetry.label(
                "Motor Mode", "speed" if IS_SPEED_MODE else "pos", True)
            while button.is_pressed():
                time.sleep(0.1)

    switcher = telemetry.create_button("switch mode", func=update_speed_mode)
    forward = telemetry.create_button("/\\")
    stopper = telemetry.create_button("-stop-")
    backward = telemetry.create_button("\\/")
    slider_adjust = telemetry.create_slider(*SLIDER, func=update_slider)
    return switcher, forward, stopper, backward, slider_adjust

def normalize(r, g, b):
    if r is None or g is None or b is None:
        return 0, 0, 0

    n = math.sqrt(r*r + g*g + b*b)
    n = 1/n if n != 0 else 0
    return r*n, g*n, b*n

def rgb_func(data, func):
    r, g, b = zip(*data)
    return func(r), func(g), func(b)

if __name__ == '__main__':
    switcher, forward, stopper, backward, slider_adjust = window_start()

    color = brick.EV3ColorSensor(3)
    pusher = brick.Motor('D')
    selector = brick.Motor('C')

    motor = selector

    brick.wait_ready_sensors(True)

    mean = 0
    std = 0
    data = []

    try:
        while True:
            if not telemetry.isopen():
                break

            if forward.is_pressed():
                sample = normalize(*color.get_rgb())
                if sample[0] > 0 and sample[1] > 0 and sample[2] > 0:
                    data.append(sample)
            if backward.is_pressed():
                data.pop()
            if stopper.is_pressed():
                data.clear()

            mean = rgb_func(data, stats.mean) if data else (0, 0, 0)
            std = rgb_func(data, stats.stdev) if len(data) > 1 else (0, 0, 0)

            telemetry.label("MOTOR_SPEED", mean, True)
            telemetry.label("MOTOR_POS", std, True)
            telemetry.label("Color", color_dist(color.get_rgb()))
            telemetry.update()
            time.sleep(0.2)
    except KeyboardInterrupt:
        exit(0)
