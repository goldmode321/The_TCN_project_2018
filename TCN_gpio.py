# These function refer to opening the relay of the car of project

import RPi.GPIO as gpio 


def init():
    gpio.setmode(gpio.BCM) # the input can be BOARD and BCM , refer to definded pin number 
    gpio.setwarnings(False) # Each time we setup a gpio pin , it will show warning . This disable the waring mechanism
    
def relay_on(pin = 4): 
    gpio.setup(4,gpio.OUT)
    gpio.output(pin,gpio.HIGH)

def relay_off(pin = 4):
    gpio.setup(4,gpio.OUT)
    gpio.output(pin,gpio.LOW)