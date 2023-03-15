from utils.brick import wait_ready_sensors, EV3UltrasonicSensor, Motor, BP
import time

# Create robot objects
color = EV3UltrasonicSensor(1)
motor = Motor("A")


def main():
    # One-time Initial Actions
    motor.set_limits(dps=180)

    while True:
        # Main Thread Loop Actions
        print(color.get_value())
        time.sleep(1)


if __name__ == '__main__':
    with wait_ready_sensors(): # Exits with KeyboardInterrupt
        main()
    print("Done with program")
