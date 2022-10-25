from utils import brick, telemetry
import time

SLIDER = [1, 360, 90]  # min, max, value

MOTOR_SPEED = 0
LAST_SPEED = 0
MOTOR_POS = 0

IS_SPEED_MODE = True

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

    ultra = brick.EV3UltrasonicSensor(3)
    pusher = brick.Motor('D')
    selector = brick.Motor('C')

    motor = selector

    try:
        while True:
            if not telemetry.isopen():
                break
            
            if IS_SPEED_MODE:
                MOTOR_POS = motor.get_position()
                if forward.is_pressed():
                    MOTOR_SPEED = slider_adjust.get_value()
                elif backward.is_pressed():
                    MOTOR_SPEED = -slider_adjust.get_value()
                elif stopper.is_pressed():
                    MOTOR_SPEED = 0

                if MOTOR_SPEED != 0:
                    LAST_SPEED = abs(MOTOR_SPEED)
                motor.set_dps(MOTOR_SPEED)
            else:
                ...
                MOTOR_POS = motor.get_position()
                MOTOR_SPEED = motor.get_speed()
                if forward.is_pressed():
                    motor.set_position(slider_adjust.get_value())
                elif backward.is_pressed():
                    motor.set_position(-slider_adjust.get_value())
                elif stopper.is_pressed():
                    motor.set_dps(0)

            
            telemetry.label("MOTOR_SPEED", MOTOR_SPEED, True)
            telemetry.label("MOTOR_POS", MOTOR_POS, True)
            telemetry.update()
            time.sleep(0.001)
    except KeyboardInterrupt:
        exit(0)
