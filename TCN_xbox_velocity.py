
#### The code below is use for controlling car with xbox and in Velocity mode

import xbox
import time
import TCN_position as tcn
import TCN_server as tcns
import TCN_velocity as tcnv
import TCN_gpio as g


# This function control the car with xbox in velocity mode
# Not applicable for position mode
def main_xbox_velocity():
    
    joy = xbox.Joystick() # joy represent xbox object
    car = tcn.init('/dev/ttyUSB1') 
    try:
        g.init()        
        g.relay_on() # turn on the power of STM32
        # Loop until back button is pressed
        while not joy.Back(): 
            try:
                x = 100*round(joy.leftX(),2) # The number from joystick is float , since  joy_stick_control_v
                y = 100*round(joy.leftY(),2) # require int input , we convert it into integer through round it to 2 decimals 
                z = 100*round(joy.rightX(),2) # and multiply by 100 
                a = int(joy.A())
                b = int(joy.B())
                #print('{} {} {}'.format(x,y,z))
                car = joy_stick_control_v(car,a,b,x,y,-z)
            except:
                g.relay_off()

    except:
        g.relay_off()
        joy.close()


# This function work with lidar . Have to run another program which has both RPLidar & UDP socket (See TCN_rplidar.py as reference)
# Run in xbox control mode if RPLidar doesn't detect any obstacle.
# Automaticly evade if any obstacle is detected. 
def main_xbox_velocity_lidar():
    joy = xbox.Joystick()
    car = tcn.init('/dev/ttyUSB1')
    sock = tcns.init_server_udp()
    try:
        g.init()        
        g.relay_on()
    # Loop until back button is pressed
        while True:

            command = tcns.listen_udp(sock)

            if command != None:
                tcnv.lidar_evade_velocity(car,command)
            else:    
                x = 100*round(joy.leftX(),2)
                y = 100*round(joy.leftY(),2)
                z = 100*round(joy.rightX(),2)
                a = int(joy.A())
                b = int(joy.B())
                #print('{} {} {}'.format(x,y,z))
                car = joy_stick_control_v(car,a,b,x,y,-z)
    except Exception as e:
        g.relay_off()
        joy.close()
        print(e)
    except KeyboardInterrupt:
        g.relay_off()
        joy.close()



# Control by velocity method *****never use with position mode******
# Input arguments : car - which is use for deliver some informations between functions ( See TCN_position.py - init() as reference )
#                   a - accelerate button
#                   b - deaccelerate button
#                   x1 - the x position of joystick
#                   y1 - the y position of joystick
#                   z1 - the x position of joystick
#                   threshold - car will move only when x or y or z position of joystick is greater than threshold
# Output arguments : car
def joy_stick_control_v(car,a,b,x1,y1,z1,threshold = 20 ): #Xbox connect with Raspberry

    car = tcn.acc_or_not(car,a,b,130)
    
    if abs(x1) < threshold:
        x1 = 0
    if abs(y1) < threshold:
        y1 = 0
    if abs(z1) < threshold:
        z1 = 0

    car[0] = int(x1*car[6]/100)
    car[1] = int(y1*car[6]/100)
    car[2] = int(z1*car[6]/100)
    #print(" {} {} {}".format(car[0],car[1],car[2]))

    car = tcn.move_to_coordinate(car)
    time.sleep(0.006)
    return car

if __name__ == '__main__':
    #main_xbox_velocity()
    main_xbox_velocity_lidar()



# This function is mainly used with TCN mapping module
# Input arguments : joy - xbox object
#                   car
# Output argument : None
def xbox_velocity_vision(joy,car):
    
    x = 100*round(joy.leftX(),2)
    y = 100*round(joy.leftY(),2)
    z = 100*round(joy.rightX(),2)
    a = int(joy.A())
    b = int(joy.B())
    car = joy_stick_control_v(car,a,b,x,y,-z)

