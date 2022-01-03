from utils.brick import BP, Motor
import time

AUX_MOTOR = Motor("C")
POWER_LIMIT = 80 # 80%
SPEED_LIMIT = 720 # 720 deg per sec (dps)

try:
    print("Motor Position Control Demo")
    AUX_MOTOR.set_power(0)

    # Encoder keeps a record of degrees turned
    AUX_MOTOR.reset_encoder()
    AUX_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)

    while True:
        speed = int(input('Enter speed:')) # Don't use eval, it's evil
        rotation = int(input('Enter rotation change (deg +/-):'))
        try:
            AUX_MOTOR.set_dps(speed)
            AUX_MOTOR.set_position_relative(rotation)
        except IOError as error:
            print(error)

except KeyboardInterrupt:
    BP.reset_all()
