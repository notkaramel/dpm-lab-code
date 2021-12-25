import time
from utils.brick import BP, EV3ColorSensor, TouchSensor, wait_ready_sensors, SensorError

# DPM Sensors and Filtering (Lecture 9) - DataLog.py
# This program is a variation on the Scan2File example with a few more
# bells and whistles to make the program more useful.  The program polls
# the EV3 Color Sensor and displays the return values on the console.  It
# allows the user to specify the SENSOR_POLL parameter as well as an optional
# output file in which the data are saved in csv format for import to a
# spreadsheet.  The program gracefully terminates when the touch sensor
# is tripped and is forced to quit when a ^C is entered on the keyboard.
# Author: F.P. Ferrie
# Date: September 19, 2021.

# Program parameters

INIT_TIME = 5                                               # Initialization time (Seconds)
SENSOR_POLL = 0.05                                          # Defaut polling rate is 50 mSec

# Allocate resources, initial configuration
T_SENSOR = TouchSensor(1)                                   # Touch sensor plugged into Port S1
C_SENSOR = EV3ColorSensor(2)                                # Color sensor plugged into Port S2

# Function to open file for logging
def fopen(fName):
    try:
        return open(fName,'w')
    except IOError:
        print('Unable to open file - aborting program.')
        BP.reset_all()


def prompt_options():
    print('BrickPi data logging program.')                      # Instructions
    print('Touch sensor in Port 1; Color sensor in Port 2.')
    print('Graceful termination when Touch sensor pressed.')
    print('Program abort (data lost) by typing ^C.')

    pDelay = SENSOR_POLL                                        # Set default rate
    
    resp = input('Override the default polling rate? y/n: ')    # Allow user to override
    if resp == 'y':
        pDelay = eval(input('Enter polling rate (units=seconds): '))
        
    resp = input('Save data to a log file? y/n: ')              # Allow save to file
    if resp == 'y':
        fName = input('Enter file name: ')
        f = fopen(fName)
    
    print('Data logged from color sensor.')
    if resp == 'y':
        f.write('Data logged from color sensor.\n')         # Print header
    
    return pDelay, resp=='y', f

try:
    # Entry point - get parameters from user.
    polling_delay, write_to_file, output_file = prompt_options()
    wait_ready_sensors()                                    # Allow motors/sensors to settle down

# Main polling loop starts here

    while True:
        try:
            sw = BP.get_sensor(T_SENSOR)                    # Read current switch state
            sw = T_SENSOR.is_pressed()
            if sw == True:                                  # If button pressed, close file and exit
                if write_to_file:
                    output_file.close
                BP.reset_all()                              # If anything other than 0, assume tripped
                
            sD = C_SENSOR.get_value()                       # Read color sensor, print values
                                                            # Read raw data [Red, Green, Blue, Intensity]
            print('{:d},{:d},{:d},{:d}'.format(sD[0],sD[1],sD[2],sD[3]))

            if write_to_file:
                  output_file.write('{:d},{:d},{:d},{:d}\n'.format(sD[0],sD[1],sD[2],sD[3]))
                  
            time.sleep(polling_delay)                              # Sleep For Polling Delay
            
            
        except SensorError as error:
            print(error)                                    # On exception, simply print error code

# ^C exit here
            
except KeyboardInterrupt:                                   # Allows program to be stopped on keyboard interrupt
    output_file.close()                                               # Close data file
    BP.reset_all()                                          # Exit program

