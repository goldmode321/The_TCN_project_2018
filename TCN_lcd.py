# Credit for this code goes to "natbett" of the Raspberry Pi Forum 18/02/13
# https://www.raspberrypi.org/forums/viewtopic.php?t=34261&p=378524
# Before running this code make sure to run sudo i2cdetect -y 1
# and match the LCD address of your device

#import smbus
#from time import *

# LCD Address
#ADDRESS = 0x3f

# commands
#LCD_CLEARDISPLAY = 0x01
#LCD_RETURNHOME = 0x02
#LCD_ENTRYMODESET = 0x04
#LCD_DISPLAYCONTROL = 0x08
#LCD_CURSORSHIFT = 0x10
#LCD_FUNCTIONSET = 0x20
#LCD_SETCGRAMADDR = 0x40
#LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
#LCD_ENTRYRIGHT = 0x00
#LCD_ENTRYLEFT = 0x02
#LCD_ENTRYSHIFTINCREMENT = 0x01
#LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
#LCD_DISPLAYON = 0x04
#LCD_DISPLAYOFF = 0x00
#LCD_CURSORON = 0x02
#LCD_CURSOROFF = 0x00
#LCD_BLINKON = 0x01
#LCD_BLINKOFF = 0x00

# flags for display/cursor shift
#LCD_DISPLAYMOVE = 0x08
#LCD_CURSORMOVE = 0x00
#LCD_MOVERIGHT = 0x04
#LCD_MOVELEFT = 0x00

# flags for function set
#LCD_8BITMODE = 0x10
#LCD_4BITMODE = 0x00
#LCD_2LINE = 0x08
#LCD_1LINE = 0x00
#LCD_5x10DOTS = 0x04
#LCD_5x8DOTS = 0x00

# flags for backlight control
#LCD_BACKLIGHT = 0x08
#LCD_NOBACKLIGHT = 0x00

#En = 0b00000100 # Enable bit
#Rw = 0b00000010 # Read/Write bit
#Rs = 0b00000001 # Register select bit

#class i2c_device:
#   def __init__(self, addr, port=1):
#      self.addr = addr
#      self.bus = smbus.SMBus(port)

# Write a single command
#   def write_cmd(self, cmd):
#      self.bus.write_byte(self.addr, cmd)
#      sleep(0.0001)

#class lcd:
   #initializes objects and lcd
#   def __init__(self):
#      self.lcd_device = i2c_device(ADDRESS)

#      self.lcd_write(0x03)
#      self.lcd_write(0x03)
#      self.lcd_write(0x03)
#      self.lcd_write(0x02)

#      self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
#      self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
#      self.lcd_write(LCD_CLEARDISPLAY)
#      self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
      #sleep(0.0001)

   # clocks EN to latch command
#   def lcd_strobe(self, data):
#      self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
      #sleep(.0005)
#      self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
      #sleep(.0001)

#   def lcd_write_four_bits(self, data):
#      self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
#      self.lcd_strobe(data)

   # write a command to lcd
#   def lcd_write(self, cmd, mode=0):
#      self.lcd_write_four_bits(mode | (cmd & 0xF0))
#      self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

   # put string function
#   def lcd_display_string(self, string, line):
#      if line == 1:
#         self.lcd_write(0x80)
#      if line == 2:
#         self.lcd_write(0xC0)
#      if line == 3:
#         self.lcd_write(0x94)
#      if line == 4:
#         self.lcd_write(0xD4)

#      for char in string:
#         self.lcd_write(ord(char), Rs)

   # clear lcd and set to home
#   def lcd_clear(self):
#      self.lcd_write(LCD_CLEARDISPLAY)
#      self.lcd_write(LCD_RETURNHOME)

#def show_string(string,line = 1):
#   l = lcd()
#   if type(string) != str:
#      print("wrong input type , input must be 'string'")
#   else:
#      l.lcd_display_string(string,line)
#def clear():
#   l = lcd()
#   l.lcd_clear()


#display = lcd()
#display.lcd_display_string("RaspiNews - 16x2", 1)
#display.lcd_display_string("I2C LCD Demo..", 2)



#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  lcd_i2c.py
#  LCD test script using I2C backpack.
#  Supports 16x2 and 20x4 screens.
#
# Author : Matt Hawkins
# Date   : 20/09/2015
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------
import smbus
import time

# Define some device parameters
I2C_ADDR  = 0x3f # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
   # Initialise display
   lcd_byte(0x33,LCD_CMD) # 110011 Initialise
   lcd_byte(0x32,LCD_CMD) # 110010 Initialise
   lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
   lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
   lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
   lcd_byte(0x01,LCD_CMD) # 000001 Clear display
   time.sleep(E_DELAY)

def lcd_byte(bits, mode):
   # Send byte to data pins
   # bits = the data
   # mode = 1 for data
   #        0 for command

   bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
   bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

   # High bits
   bus.write_byte(I2C_ADDR, bits_high)
   lcd_toggle_enable(bits_high)

   # Low bits
   bus.write_byte(I2C_ADDR, bits_low)
   lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
   # Toggle enable
   time.sleep(E_DELAY)
   bus.write_byte(I2C_ADDR, (bits | ENABLE))
   time.sleep(E_PULSE)
   bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
   time.sleep(E_DELAY)

def lcd_string(message,line): # line is either 1 or 2 for us 
   # Send string to display

   message = message.ljust(LCD_WIDTH," ")

   lcd_byte(line, LCD_CMD)

   for i in range(LCD_WIDTH):
      lcd_byte(ord(message[i]),LCD_CHR)


#=========== Example function ==============

def main():
   # Main program block

   # Initialise display
   lcd_init()

   while True:

      # Send some test
      lcd_string("RPiSpy         <",LCD_LINE_1)
      lcd_string("I2C LCD        <",LCD_LINE_2)

      time.sleep(3)

      # Send some more text
      lcd_string(">         RPiSpy",LCD_LINE_1)
      lcd_string(">        I2C LCD",LCD_LINE_2)

      time.sleep(3)

if __name__ == '__main__':
   main()