import time
import serial
import os
import math
import TCN_server as tcns
import TCN_position as tcnp

# Funtion is almost the same with the one in TCN_position
# The difference is it is design to work with velocity mode


def init(port = '/dev/ttyUSB1'): 
    ser = serial.Serial(port,115200)
    ser.write([0xFF,0xFE,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00]) # Return to origin
    xpos = 0
    ypos = 0
    zpos = 0

    dir_byte = 0
    number_of_command = 0
    step = 1
    car =  [ xpos , ypos , zpos ,  dir_byte , ser , number_of_command , step]
    #         0       1     2          3       4           5              6        7           8    
    #Check is record file exist and clear data if there are some already store in there
    try:
        if os.stat('last_position_input.txt').st_size != 0:
            f1 = open('last_position_input.txt','w')
            f1.close()
        if os.stat('history_position_input.txt').st_size !=0:
            f2 = open('history_position_input.txt','w')
            f2.close()
    except FileNotFoundError:
            f1 = open('last_position_input.txt','w')
            f1.close()
            f2 = open('history_position_input.txt','w')
            f2.close()                    
    tcnp.record_position(car)

    return car

# While the name is refer to position , it is actually the velocity 
# Input argument : car
#                   x - the velocity of x direction
#                   y - the velocity of y direction
#                  max_speed - the max value is 131 (Encoder)
# Output argument : car
def set_target_velocity(car,x,y,z,max_speed = 50):
    posx = 0
    posy = 0
    posz = 0
    lastx = x
    lasty = y
    lastz = z
    x = x - car[0]
    y = y - car[1]
    z = z - car[2]
    print('xx {} yy {} zz {}'.format(x,y,z))
    dis = (x**2 + y**2)**0.5 # Encoder
    angle = tcnp.vector_angle(x,y)

    loop_int = int(dis/max_speed)
    loop_float = dis/max_speed
    dis_left = int(max_speed*(loop_float - loop_int))
    for i in range(loop_int):
        if abs(x) > 0:
            car[0] = int(round(max_speed*math.cos(angle),0))                    
        if abs(y) > 0:
            car[1] = int(round(max_speed*math.sin(angle),0))
        if abs(z) > 0:
            if z > 0:
                car[2] = max_speed
            if z < 0:
                car[2] = -max_speed

        #print("x {} y {} z {}".format(posx,posy,posz))
        tcnp.move_to_coordinate(car)

        time.sleep(0.006)
    car[0] = car[1] = car[2] = 0
    tcnp.move_to_coordinate(car) 
    car[0] = lastx
    car[1] = lasty
    car[2] = lastz
    return car




def set_target_position_lidar(car,sock,x,y,z,max_speed = 50):
    command = tcns.listen_udp(sock)
    posx = 0
    posy = 0
    posz = 0
    lastx = x
    lasty = y
    lastz = z
    x = x - car[0]
    y = y - car[1]
    z = z - car[2]
    print('xx {} yy {} zz {}'.format(x,y,z))
    dis = (x**2 + y**2)**0.5 # Encoder
    angle = tcnp.vector_angle(x,y)

    loop_int = int(dis/max_speed)
    loop_float = dis/max_speed
    dis_left = int(max_speed*(loop_float - loop_int))
    for i in range(loop_int):
        if command != None:
            car = lidar_evade_velocity(car,command)
            car=set_target_position_lidar(car,sock,lastx+car[0],lasty+car[1],z,max_speed)
            print('evading')
            return 0
        else:
            if abs(x) > 0:
                car[0] = int(round(max_speed*math.cos(angle),0))                    
            if abs(y) > 0:
                car[1] = int(round(max_speed*math.sin(angle),0))
            if abs(z) > 0:
                if z > 0:
                    car[2] = max_speed
                if z < 0:
                    car[2] = -max_speed

            #print("x {} y {} z {}".format(posx,posy,posz))
            tcnp.move_to_coordinate(car)

            time.sleep(0.006)
    car[0] = car[1] = car[2] = 0
    tcnp.move_to_coordinate(car) 
    car[0] = lastx
    car[1] = lasty
    car[2] = lastz
    return car





# Evade obstacle  , only work for velocity mode
def lidar_evade_velocity(car,command, step = 30):
    d = int(command[1:5])
    a = int(command[6:10])
    #if 180 > a >= 0:
    #    a = a -30
    #if 360 >= a > 180:
    #    a = a + 30
    dx = int(round(step*math.sin(math.radians(a)),0))
    dy = int(round(step*math.cos(math.radians(a)),0))
    car[0] = -dx
    car[1] = -dy
    tcnp.move_to_coordinate(car)
    #car = move_to_coordinate(car)
    time.sleep(0.1)
    print('dx {} dy {} a {} d {}'.format(dx,dy,a,d))
    return car




#**********************************************
#           main function + test
#************************************************

def set_target_velocity_main():
    car = init()
    while True:
        x = int(input('enter x'))
        y = int(input('enter y'))
        car = set_target_velocity(car,x,y,0,50)

def set_target_velocity_lidar_main():
    car = init()
    sock = tcns.init_server_udp()
    while True:
        #x = int(input('enter x'))
        y = int(input('enter y'))
        car = set_target_position_lidar(car,sock,0,y,0,20)

if __name__ == '__main__':
    #set_target_velocity_main()
    set_target_velocity_lidar_main()