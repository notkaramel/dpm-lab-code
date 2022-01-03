# BrickPi Programming

We will always use `python3` to execute BrickPi scripts, don't forget that.  


First step is to initialize the robot part of your BrickPi:  

```python
from utils import brick

BP = brick.Brick() # BP is just a name

... # Do actions with robot

BP.reset_all() # Must end with this to turn off robot and motors
```

Then create motors and sensors depending on what is in your ports:

```python
touch1 = brick.TouchSensor(BP, 1) # Button sensor, port S1
us1 = brick.EV3UltrasonicSensor(BP,3) # port S3
color1 = brick.EV3ColorSensor(BP,2) # port S2
gyro1 = brick.EV3GyroSensor(BP, 4) # port S4

motLeft = brick.Motor(BP, 'B') # Motor in port MB
motRight = brick.Motor(BP, 'C') # port MC
```

# Sensors in General

Every sensor has a `sensor.get_value()` method:

```python
isPressed = touch1.get_value() # 0 or 1, integer

distance = us1.get_value() # 0 to 255, centimeter, float

colors = color1.get_value() # [r,g,b,x], 4 floats (x is unknown)

rotation = gyro1.get_value() # [abs, dps], Absolute Degrees Rotated 
                             # and Degrees Per Second, floats
```

## Sensor Mode

Each sensor also has several modes (except Touch sensor):

```python
### Color sensor has 'component','ambient','red','rawred','id'

# Create sensor with mode:
color2 = brick.EV3ColorSensor(BP, 2, mode='red')

# OR change the sensor mode:
color2.set_mode('id')
```

# Motors in General

There are 3 physical motor types, but one `Motor` class only.  
Motors use degrees as units, and power value from `-100 to 100`

If a motor is moving, it will stay moving, until you tell it to stop. **You must tell motors to stop `power=0`**

```python
motLeft.set_power(50)
motRight.set_power(-50)

motLeft.set_power(0)  # A program without these will have motors
motRight.set_power(0) # moving after the program has exited
```

## Motor Status

```python
status = motLeft.get_status()

# list of [bit_flags, power, encoder, dps]
# power= -100 to 100
# encoder= degrees rotated
# dps= actual rotation speed, degree/second
```