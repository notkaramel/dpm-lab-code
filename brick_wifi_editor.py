import os
import sys
from tkinter import COMMAND

ORIGINAL_WPA = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=CA\n\nnetwork={\n\tssid="DPM"\n\tpsk="dddpppmmm"\n\tkey_mgmt=WPA-PSK\n}\n'

NETWORK = '''network=[
    ssid="{}"
    psk="{}"
    key_mgmt=WPA-PSK
]\n'''

def reset_autohotspot():
    os.system("printf '6\n1\nrobots1234\n8\n' | ~/Autohotspot/autohotspot-setup.sh")

def reset_wpa():
    os.system(f"printf '{ORIGINAL_WPA}' | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.new.conf")

def set_wpa(text):
    os.system(f"printf '{text}' | sudo tee /etc/wpa_supplicant/wpa_supplicant.conf")

def get_wpa():
    f = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'r')
    s = f.read()
    f.close()
    return s

def new_network(ssid, psk):
    s = NETWORK.format(ssid, psk)
    s = s.replace('[', '{')
    s = s.replace(']', '}')
    return s

def add_network(ssid, psk):
    set_wpa(get_wpa() + new_network(ssid, psk))


COMMAND_OPTIONS = '''
Your options include:

1 - Delete all stored wifi networks, reset to default
2 - Add a Wifi network (those that only uses a single password)
3 - Make this Brick connect to another Host Brick's Wifi Hotspot only
4 - Connect to a Wifi Network if Available (this action exits this script)
5 - List the current networks that are available
6 - Exit this script

Input your choice: '''
def main():
    try:
        print("This script is a utility for reconfiguring this current brick's wifi.")

        while True:
            choice = input(COMMAND_OPTIONS)
            if choice == '1':
                print("(WARNING: This will delete all previously added wifi networks)")
                input("Okay? (Press Enter to Continue...)")
                print("Deleting all known networks...")
                reset_wpa()
                print("Command successful.")
            elif choice == '2':
                try:
                    print("(WARNING: This will store the network's password in plaintext)")
                    input("Okay? (Press Enter to Continue...)")
                    ssid = input("What is the network's name? ")
                    psk  = input("What is the network's password? ")
                    add_network(ssid, psk)
                    print("Command successful.")
                except KeyboardInterrupt:
                    print("Add Network Cancelled...")
            elif choice == '3':
                try:
                    print("(WARNING: This action will make the Host Brick's hotspot, the only network that this client Brick connects to)")
                    input("Okay? (Press Enter to Continue...)")
                    print("Resetting all known Wifi Networks...")
                    reset_wpa()
                    print("Reset successful.")
                    brick_num = input('What is the number of the Host BrickPi you wish to connect to? ')
                    print(f"Adding new network: 'dpm-{brick_num}-hotspot'")
                    add_network(f'dpm-{brick_num}-hotspot', '1234567890')
                    print("Command successful.")
                except KeyboardInterrupt:
                    print("Add Network Cancelled...")
            elif choice == '4':
                reset_autohotspot()
            elif choice == '5':
                print(get_wpa())
            elif choice == '6':
                print("Script ended.")
                return
            else:
                print("Invalid Command Received...")
            print()
    except KeyboardInterrupt:
        return


if __name__=='__main__':
    main()