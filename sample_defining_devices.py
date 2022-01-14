from utils.brick import configure_ports, TouchSensor, EV3ColorSensor, EV3UltrasonicSensor, EV3GyroSensor, Motor, wait_ready_sensors


T_SENSOR, C_SENSOR, US_SENSOR, GYRO_SENSOR, MOTOR1, MOTOR2, MOTOR3 = configure_ports(
    PORT_1=TouchSensor, PORT_2=EV3ColorSensor, PORT_3=EV3UltrasonicSensor, PORT_4=EV3GyroSensor, PORT_A=Motor, PORT_B=Motor, PORT_C=Motor)

######################################################

T_SENSOR, C_SENSOR, US_SENSOR, GYRO_SENSOR = configure_ports(
    PORT_1=TouchSensor, PORT_2=EV3ColorSensor, PORT_3=EV3UltrasonicSensor, PORT_4=EV3GyroSensor)
M1, M2, M3 = Motor.create_motors("ABC")

######################################################

T_SENSOR, C_SENSOR = TouchSensor(1), EV3ColorSensor(2)
US_SENSOR, GYRO_SENSOR = EV3UltrasonicSensor(3), EV3GyroSensor(4)
M1, M2, M3 = Motor('A'), Motor('B'), Motor('C')

wait_ready_sensors()
