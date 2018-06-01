
# This program work with any type of joystick directly , and it must can output the position of stick with numbers.
# This is design with Xbox , 'a' button represent accelerate , while 'b' is opposite . x1,y1 is left stick position
#  z1 is the x-axis of right stick
# The moving method is by "adding value" of each axis


import xbox
import time
import TCN_position as tcn
import TCN_server as tcns

def main_xbox_position():  
    joy = xbox.Joystick()
    car = tcn.init('/dev/ttyUSB1')

    # Loop until back button is pressed
    while not joy.Back():
        
        #print(start)
        x = 100*round(joy.leftX(),2)
        y = 100*round(joy.leftY(),2)
        z = 100*round(joy.rightX(),2)
        a = int(joy.A())
        b = int(joy.B())
        car = joy_stick_control_2(car,a,b,x,y,-z)

    joy.close()


# Format floating point number to string format -x.xxx
def fmtFloat(n):
    return '{:6.3f}'.format(n)  

# In position mode , control with xbox connect to Rapberry pi ( wire or unwire )  
def joy_stick_control_2(car,a,b,x1,y1,z1,start=0,threshold = 20 , change_mode = 1): #Xbox connect with Raspberry

    car = tcn.acc_or_not(car,a,b) # determine the incresement or decresement of step

    if abs(x1) < threshold:
        x1 = 0
    if abs(y1) < threshold:
        y1 = 0
    if abs(z1) < threshold:
        z1 = 0

    xyz = [abs(x1*car[6]/100),abs(y1*car[6]/100),abs(z1*car[6]/100)]

    car[0] = int(car[0] + x1*car[6]/100)
    car[1] = int(car[1] + y1*car[6]/100)
    car[2] = int(car[2] + z1*car[6]/100)


    car = tcn.move_to_coordinate(car)
    tcn.record_position(car)
    time.sleep(0.006)
    return car




if __name__ == '__main__':
    main_xbox_position()
