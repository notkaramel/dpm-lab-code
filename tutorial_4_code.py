from utils import fakebrick, telemetry
import time

MOTOR_SPEED = [1440, 1, 10, 1440 // 2, 0]
MOTOR_POS   = [720, 1, 10, 90, 0]

def window_start():
    telemetry.start()
    telemetry.resize(500,500)

    telemetry.label("Speed Delta", MOTOR_SPEED[3], True)
    telemetry.label("Speed Current", MOTOR_SPEED[4], True)
    telemetry.label("Pos Delta", MOTOR_SPEED[4], True)
    telemetry.label("Pos Current", MOTOR_SPEED[4], True)

    def update_speed_delta(slider:telemetry._Slider, *args):
        MOTOR_SPEED[3] = telemetry.remote(slider.get_value)
        telemetry.remote(telemetry.label, "Speed Delta", MOTOR_SPEED[3], True)

    def update_pos_delta(slider:telemetry._Slider, *args):
        MOTOR_POS[3] = telemetry.remote(slider.get_value)
        telemetry.remote(telemetry.label, "Pos Delta", MOTOR_POS[3], True)

    forward = telemetry.create_button("/\\")
    backward = telemetry.create_button("\\/")
    speed_adjust = telemetry.create_slider(MOTOR_SPEED[1], MOTOR_SPEED[0], MOTOR_SPEED[3], func=update_speed_delta)
    pos_adjust = telemetry.create_slider(MOTOR_POS[1], MOTOR_POS[0], MOTOR_POS[3], func=update_pos_delta)
    return forward, backward, speed_adjust

if __name__=='__main__':
    forward, backward, speed_adjust = window_start()

    motor = Motor('A')

    try:
        while True:
            if not telemetry.isopen():
                break
            MOTOR_SPEED[4] = 0
            if forward.is_pressed():
                MOTOR_SPEED[4] += MOTOR_SPEED[3]
            if backward.is_pressed():
                MOTOR_SPEED[4] -= MOTOR_SPEED[3]
            telemetry.label("Speed Current", MOTOR_SPEED[4], True)



            telemetry.update()
            time.sleep(0.001)
    except KeyboardInterrupt:
        exit(0)
