from utils.brick import wait_ready_sensors, EV3ColorSensor, EV3UltrasonicSensor, TouchSensor

color = EV3ColorSensor(1) # port S1
touch = TouchSensor(2) # port S2
ultra = EV3UltrasonicSensor(3) # port S3

# waits until every previously defined sensor is ready
wait_ready_sensors()

"""
Every sensor has a 'sensor.get_value()' method, 
returning different things for different sensors.

all sensors give 'None' when there is an error
"""
color.get_raw_value() # usually list [r,g,b,intensity], sometimes one number
touch.get_raw_value() # 0 or 1
ultra.get_raw_value() # usually distance, centimeters



#######################
###                 ###
### COLOR DETECTION ###
###                 ###
#######################

"""The color sensor has several modes to detect colors, here are two useful ones"""

"""
{ID mode} uses a built-in detection function, and gives you a color name
(e.g. "red", "orange", "violet")
* very quick and simple
* but not exactly reliable
* often wrong

Returns "unknown" when facing an error, or an unkown color
"""
color_name = color.get_color_name()
print(color_name)

"""
{Component mode} gives RGB values, a list of Red, Green, and Blue
* reliable, more info
* needs custom function to determine a color profile
* great for just reading one type of color

Returns a list of [None, None, None] on error
values range from 0 to 255
"""
rgb_list = color.get_rgb()
print(rgb_list)

############################
###                      ###
### ULTRASONIC DETECTION ###
###                      ###
############################
"""The Ultrasonic Sensor has two main modes, and one extra that we don't use generally"""

"""{Centimeter mode} reads the distance in centimeters. Returns a float value."""
distance = ultra.get_cm()
print(distance)

"""{Inches mode} still reads distance but gives back inches. Also a float value."""
distance = ultra.get_inches()
print(distance)

"""{Detection mode} uses ultrasonic sensor to detect other ultrasonic sensors. Output boolean."""
ultra.detects_other_us_sensor()