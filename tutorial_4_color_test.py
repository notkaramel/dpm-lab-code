from utils import brick, telemetry
import statistics as stats
import time
import math

SLIDER = [0, 720, 90]  # min, max, value

MOTOR_SPEED = 0
LAST_SPEED = 0
MOTOR_POS = 0

IS_SPEED_MODE = True

positions = [-70, -160, -255, -360, -450, -545] # 0 is starting pos. use 90dps.
reset_distance = 600

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
            telemetry.label("Motor Mode", "speed" if IS_SPEED_MODE else "pos", True)
            while button.is_pressed():
                time.sleep(0.1)
        

    switcher = telemetry.create_button("switch mode", func=update_speed_mode)
    forward = telemetry.create_button("/\\")
    stopper = telemetry.create_button("-stop-")
    backward = telemetry.create_button("\\/")
    slider_adjust = telemetry.create_slider(*SLIDER, func=update_slider)
    return switcher, forward, stopper, backward, slider_adjust


if __name__ == '__main__':
    switcher, forward, stopper, backward, slider_adjust = window_start()

    color = brick.EV3ColorSensor(3)
    pusher = brick.Motor('D')
    selector = brick.Motor('C')

    motor = selector

    brick.wait_ready_sensors(True)

    mean = 0
    std  = 0
    data = []

    def normalize(r,g,b):
        if r is None or g is None or b is None:
            return 0,0,0

        n = math.sqrt(r*r + g*g + b*b)
        n = 1/n if n != 0 else 0
        return r*n, g*n, b*n

    try:
        while True:
            if not telemetry.isopen():
                break
            
            if forward.is_pressed():
                sample = normalize(*color.get_rgb())
                if sample[0] > 0 and sample[1] > 0 and sample[2] > 0:
                    data.append(sample)
            if backward.is_pressed():
                data.remove()
            if stopper.is_pressed():
                data.clear()
            mean = stats.mean(data)
            std = stats.stdev(data)
            time.sleep(1)


            
            telemetry.label("MOTOR_SPEED", mean, True)
            telemetry.label("MOTOR_POS", std, True)
            telemetry.update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        exit(0)
