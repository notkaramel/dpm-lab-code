from utils.brick import wait_ready_sensors, EV3ColorSensor, EV3UltrasonicSensor, TouchSensor

color = EV3ColorSensor(1) # port S1
touch = TouchSensor(2) # port S2
ultra = EV3UltrasonicSensor(3) # port S3

# waits until every previously defined sensor is ready
wait_ready_sensors()

"""
Every sensor has a 'sensor.get_value()' method, 
returning different things for different sensors

all sensors give 'None' when there is an error
"""
color.get_value() # usually list, sometimes one number
touch.get_value() # 0 or 1
ultra.get_value() # usually distance, centimeters



#######################
###                 ###
### COLOR DETECTION ###
###                 ###
#######################

"""The color sensor has several modes to detect colors, here are two useful ones"""

"""
ID mode uses a built-in detection function, and gives you a color name
(e.g. "red", "orange", "violet")
* very quick and simple
* but not exactly reliable
* often wrong

Returns "unknown" when facing an error, or an unkown color
"""
color_name = color.get_color_name()
print(color_name)

"""
Component mode gives RGB values, a list of Red, Green, and Blue
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
