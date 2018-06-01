# Example 1: Absolute coordinate 
# 
# import TCN_position as tcn
# 
# def main():
#     port = '/dev/ttyUSB1' # it may be ttyUSB0
#     car = tcn.init(port)
#     while True:
#         x = int(input('enter x'))
#         y = int(input('enter y'))
#         z = int(input('enter z'))
#         car = tcn.set_target_position(car,x,y,z)
#
# if __name__ == '__main__':
#    main()
#--------------------------------------------------------------
# Example 2: trace route 
#
# import TCN_position as tcn
#
# port = '/dev/ttyUSB1'
# tcn.trace_return(port)
#--------------------------------------------------------------
#Example 3 : control with xbox 1
#import xbox
#import TCN_position as tcn
#
# #Loop until back button is pressed
#while not joy.Back():
#
#    x = 100*round(joy.leftX(),2)
#    y = 100*round(joy.leftY(),2)
#    z = 100*round(joy.rightX(),2)
#    a = int(joy.A())
#    b = int(joy.B())
#
#    print('x = {}'.format(x))
#    print('y = {}'.format(y))
#    print('z = {}'.format(z))
#    if a ==1:
#        print(a)
#    if b ==1:
#        print(b)
#    car = tcn.joy_stick_control_2(car,a,b,x,y,z)
#--------------------------------------------------------------

import time
import serial
import os
import math
import TCN_server as tcns
import socket
import TCN_lcd as tcnl
import TCN_gpio as tcng


####################################################
#             General Function
####################################################

# Function init is greatly recommended to be used at first if you start a new program
# This function orders the car to return its origin(Encoder) , creates new command-recording-file
# and builds a very important variable 'car' . this variable is commenly used in functions below
# Input arguments : port - the port of RPLidar
# Output argument : car - which is use for deliver some informations between functions
def init(port = '/dev/ttyUSB1'): 
    ser = serial.Serial(port,115200)
    ser.write([0xFF,0xFE,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]) # Make the car return to origin at first (Encoder).
    xpos = 0 
    ypos = 0
    zpos = 0
    dir_byte = 0
    number_of_command = 0
    step = 1
    car =  [ xpos , ypos , zpos ,  dir_byte , ser , number_of_command , step]
    #         0       1     2          3       4           5              6        7           8    




    # Code below turn on the power of STM32 (through relay , on GPIO pin 4 )
    # And it will initialize the LCD screen
    #
    tcng.init()     # Initialize GPIO
    tcng.relay_on() # Turn on relaya
    tcnl.lcd_init() # Initialize LCD screen
    print('program start in 2 second') # STM32 needs about 2~3 second to launch
    time.sleep(2)



    # Code below create the record file , the content of 'history_position_input.txt' will be the position that orders STM32 to move.
    # While 'last_position_input.txt' only record the position input of that moment.
    try:
        if os.stat('last_position_input.txt').st_size != 0: # If file exist , check if there is any content exist.
            f1 = open('last_position_input.txt','w')        # If it does , clean the file
            f1.close()
        if os.stat('history_position_input.txt').st_size !=0:
            f2 = open('history_position_input.txt','w')
            f2.close()
    except FileNotFoundError:                                   # It will raise 'FileNotFoundError' if file doesn't exist , 
            f1 = open('last_position_input.txt','w')            # Create new file .
            f1.close()
            f2 = open('history_position_input.txt','w')
            f2.close()                    
    # Additional remark : The better way is use 2 "try - except" to check each file . 

    record_position(car) # Save the initial position command into recording file upward.

    return car # car[] will be used in many function below . Any function refer to "moving the car " will require this variable.



# Move car to the desired coordinate . If z is required , it must be noted that this function  move z (turnning) first . 
# Since the control method is base on "coordinate" . It should be noted that the way to make car move faster is by 
# increasing the "step"(coordinate) in the same cycle time. max step is limit under 
# @@@@@@ The acceleration method still havn't fully ready . 
# Input arguments : car
#                    x  - Target x position
#                    y  - Target x position
#                    z  - Target x position
#                   time_delay_on - If true , car will wait until moving to target position ( no use in accelerate mode)
#                   accelerate - If is 1 ,trigger accelerate mode
#                   acc_time - the time needed to go to max speed . Only needed if accelerate = 1
#                   max_step - 0~32(Encoder) , it is recommended that do not exceed 32. Only needed if accelerate = 1
#                   ini_step - Initial velocity (Encoder). Only needed if accelerate = 1 
def set_target_position(car, x , y , z , time_delay_on = True , accelerate = 0 ,acc_time = 1 ,max_step = 32,ini_step = 0):
    
    if abs(z) > 0: # if z is required , move to z coordinate first 
        car[2] = z            
        car = move_to_coordinate(car)
        if time_delay_on == True:
            time_delay = calculate_time_delay(0,0,z,car)        
            time.sleep(time_delay)
    
    if accelerate == 0: # When not using accelerate method

        car[0] = x
        car[1] = y            
        car = move_to_coordinate(car)
        if time_delay_on == True:
            time_delay = calculate_time_delay(x,y,0,car)        
            time.sleep(time_delay)
        return car

    # Note that acceleration must have time delay . Thus, time_delay_on option is no use in thise mode. 
    if accelerate == 1:
        step = 0  # step represent the real time step
        
        # We can get target vector from code below
        dx = x - car[0] # Get the length of x between target and the one at the moment
        dy = y - car[1]
        dz = z - car[2]

        target_length = (dx**2 + dy**2)**0.5 # Calculate the distance

        angle = vector_angle(dx,dy) # get the vector angle
        acc_dis = acc_calculate_total_displacement(acc_time, max_step, ini_step) # Calculate the total displacement needed for accelerate method
        print('{} {}'.format(target_length,acc_dis))
        loop_num_middle = int((target_length - 2*acc_dis)/max_step) # When speed reach maximum , and if we still move car with 1 step each command
                                                                    # we have to know number of times needed to move to deaccelerate position  

        pos_deaccX = car[0] + int(round((target_length - acc_dis)*math.cos(angle),0)) # The x position of deacceleration
        pos_deaccY = car[1] + int(round((target_length - acc_dis)*math.sin(angle),0)) # The y position of deacceleration     

        print('{} {}'.format(pos_deaccX,pos_deaccY))


        # if acc_dis is larger than target_length , then we should use other method
        # Since by this method , the car will always go to its max speed then hold the speed ,and finally slow down.
        # If the situation is false , and we do use the same method . The car will overshoot . 
        if ( target_length / 2 ) >= acc_dis:
            
            # First stage acceleration : start accelerating
            car = acc_by_time(car,angle,acc_time, max_step, ini_step)
            print('stage 1 complete')

            # Third stage : steady step rate until deaccelerate
            for i in range(loop_num_middle):
                deltaX = int(round(max_step*math.cos(angle),0))
                deltaY = int(round(max_step*math.sin(angle),0))
                car[0] = car[0] + deltaX
                car[1] = car[1] + deltaY
                car = move_to_coordinate(car)        
                #print('x {} y {} time {} step {}'.format(car[0],car[1],time_delay,step))
                time.sleep(0.006)
            print('stage 3 complete')

            # Fourth stage : go to deaccelrate position
            car[0] = pos_deaccX
            car[1] = pos_deaccY
            car = move_to_coordinate(car)
            print('stage 4 complete')

            # Fifth stage : start deaccelerating
            car = deacc_by_time(car,angle,acc_time, max_step, ini_step)
            print('final stage complete')

            return car 

        if ( target_length / 2 ) < acc_dis:    

            # first stage : generate new max_step
#            half_length = 0
#            times = 0
#            max_step = 0
#            while half_length < (target_length/2):
#                times = times + 1
#                half_length = half_length + acc_rate*times
#            max_step = acc_rate * times
#            print(max_step)

            print('stage 1 complete')

            # Second stage : accelerate



            # Third stage : deaccelerate


            # Final stage : final position

            car[0] = x
            car[1] = y
            car = move_to_coordinate(car)
            time_delay = calculate_time_delay(x,y,0,car)        
            print('x {} y {} time {} step {}'.format(car[0],car[1],time_delay,step))
            time.sleep(time_delay)
            print('final stage complete') 
            print(car[0],car[1])
            return car 


# This function , I try to combine "lidar envation" with "Position control mode" but didn't work well  
#
def set_target_position_lidar(car,sock, x , y , z ,acc_time = 0.5 ,max_step = 32,ini_step = 0):
    sock = tcns.init_server_udp()
    command = tcns.listen_udp(sock,11)
    if command != None:
        command = command.decode('utf-8')
        lidar_evade(car,command,0,200) 
    else:
        step = 0  # step represent the real time step
        dx = x - car[0]
        dy = y - car[1]
        dz = z - car[2]
        target_length = (dx**2 + dy**2)**0.5

        angle = vector_angle(dx,dy)
        acc_dis = acc_calculate_total_displacement(acc_time, max_step, ini_step)
        print('{} {}'.format(target_length,acc_dis))
        loop_num_middle = int((target_length - 2*acc_dis)/max_step)

        pos_deaccX = car[0] + int(round((target_length - acc_dis)*math.cos(angle),0)) # The position of deacceleration
        pos_deaccY = car[1] + int(round((target_length - acc_dis)*math.sin(angle),0))       

        print('{} {}'.format(pos_deaccX,pos_deaccY))


        # if acc_dis is larger than target_length , then we should use other method
        if ( target_length / 2 ) >= acc_dis:
            
            # First stage acceleration : start accelerating
            car = acc_by_time(car,angle,acc_time, max_step, ini_step)
            print('stage 1 complete')

            # Third stage : steady step rate until deaccelerate
            for i in range(loop_num_middle):
                if command != None:
                    command = command.decode('utf-8')
                    lidar_evade(car,command,0,200)
                    loop_num_middle = loop_num_middle + 1
                else:
                    deltaX = int(round(max_step*math.cos(angle),0))
                    deltaY = int(round(max_step*math.sin(angle),0))
                    car[0] = car[0] + deltaX
                    car[1] = car[1] + deltaY
                    car = move_to_coordinate(car)        
                #print('x {} y {} time {} step {}'.format(car[0],car[1],time_delay,step))
                time.sleep(0.006)
            print('stage 3 complete')

            # Fourth stage : go to deaccelrate position
            car[0] = pos_deaccX
            car[1] = pos_deaccY
            car = move_to_coordinate(car)
            print('stage 4 complete')

            # Fifth stage : start deaccelerating
            car = deacc_by_time(car,angle,acc_time, max_step, ini_step)
            print('final stage complete')



# The most basic method of obstacle-avoidance method . Input [ distance , angle ] from RPLidar with formation : D0000A0000N
# calculate to the next coordinate the car should move and run . 
# Input arguments : car
#                   command - the data from RPLidar which is sent by socket ( See TCN_rplidar as reference)
#                   division - currently no use.
#                   step - the distance of car to run away (Encoder).
def lidar_evade(car,command , division = 0 , step = 200 ):
    d = int(command[1:5]) # lowest distance of obstacle
    a = int(command[6:10]) # the related angle of car and obstacle 

    if 180 > a >= 0:
        a = a -30
    if 360 >= a > 180:
        a = a + 30

    dx = int(round(step*math.sin(math.radians(a)),0)) # You may found it strange that " a (angle)" had been added 30 or -30 and I use " distance * sin " as the step x to move
    dy = int(round(step*math.cos(math.radians(a)),0)) # My theory is the make car go left or right to avoid car keep sticking with obstacle
                                                      # Although it didn't work that well

    car[0] = car[0] - dx # dx substract from current x , to have target x
    car[1] = car[1] - dy
    move_to_coordinate(car)
    print('dx {} dy {} a {} d {}'.format(dx,dy,a,d))
    return car


# This function make car control by keyboard , the moving method is base on the increment or decrement of x-y coordinate
# Input arguments : keyboard - Input key from keyboard (string)
#                     car
#                   stepping - 0 , 1 or 2
# Output argument : car
def direct_control(keyboard ,car ,stepping = 0):
    
    if stepping == 0:
        pass
    elif stepping == 1:
        car[6] = car[6] + 10
        print('+ {}'.format(car[6]))
    elif stepping == 2:
        car[6] = car[6] - 10
        print('+ {}'.format(car[6]))

    if keyboard == 's':
        pass
    elif keyboard == 'd':
        car[0] = car[0] + car[6]
    elif keyboard == 'w':
        car[1] = car[1] + car[6]
    elif keyboard == 'a':
        car[0] = car[0] - car[6]
    elif keyboard == 'x':
        car[1] = car[1] - car[6]
    elif keyboard == 'e':
        car[0] = car[0] + car[6]
        car[1] = car[1] + car[6]
    elif keyboard == 'z':
        car[1] = car[1] - car[6]
        car[0] = car[0] - car[6]
    elif keyboard == 'q':
        car[1] = car[1] + car[6]
        car[0] = car[0] - car[6]
    elif keyboard == 'c':
        car[1] = car[1] - car[6]
        car[0] = car[0] + car[6]

    car = move_to_coordinate(car)
    record_position(car)
    time.sleep(car[6]/4600)
    return car

# This function read the histroy file to rerun the whole route
####### Only work with position mode
# Input argument : port - the port of STM32 controller
# Output argument : car
def trace_return(port):
    ser = serial.Serial(port,115200)
    car = [ 0 , 0 , 0 , 0 , ser , 0]
#           x   y   z  dir            
    i = 0
    file = open('history_position_input.txt')
    position = file.readlines()
    position.reverse()

    for i in range(1,len(position)):

        x = ''
        y = ''
        z = ''
        xpos = position[i].find('X')
        ypos = position[i].find('Y')
        zpos = position[i].find('Z')
        epos = position[i].find('E')

        for a in range(xpos+1,ypos-1):
            x = x + position[i][a]           

        for j in range(ypos+1,zpos-1):
            y = y + position[i][j]           

        for k in range(zpos+1,epos-1):
            z = z + position[i][k]
        x = int(x)
        y = int(y)
        z = int(z)

        inix = ''
        iniy = ''
        iniz = ''
        inixpos = position[i-1].find('X')
        iniypos = position[i-1].find('Y')
        inizpos = position[i-1].find('Z')
        iniepos = position[i-1].find('E')
        for a in range(inixpos+1,iniypos-1):
            inix = inix + position[i-1][a]         

        for j in range(iniypos+1,inizpos-1):
            iniy = iniy + position[i-1][j]         

        for k in range(inizpos+1,iniepos-1):
            iniz = iniz + position[i-1][k]
        inix = int(inix)
        iniy = int(iniy)
        iniz = int(iniz)

        #displacement = ( (x-inix)**2 + (y-iniy)**2 + (z-iniz)^2 )**0.5
        #time_delay = displacement/4800
        car[0] = x
        car[1] = y
        car[2] = z
        time_delay = calculate_time_delay(inix,iniy,iniz,car)
        #print(car)
        car = move_to_coordinate(car)
        #print(time_delay)
        time.sleep(time_delay)

    file.close()

    return car

# THIS ONE STILL NOT READY YET
# Function below refer to basic velocity control in 'Absolute postion control'
# the variable 'car' can be get from any function that output 'car'
def set_target_position_adding(car,x,y,z,step = 300): 
        
    last_position = [car[0],car[1],car[2]]

    dx_sum = x - car[0]
    dy_sum = y - car[1]
    dz_sum = z - car[2]
    #print('{} {} {}'.format(dx_sum,dy_sum,dz_sum))

# the adding rate of each axis
    dx = round(dx_sum / step)
    dy = round(dy_sum / step)
    dz = round(dz_sum / step)
    #print('{} {} {}'.format(dx,dy,dz))

    processflag = 0

    while processflag < step:
        
        lastx = car[0]
        lasty = car[1]
        lastz = car[2]
        car[0] = car[0] + dx
        car[1] = car[1] + dy
        car[2] = car[2] + dz
        time_delay = calculate_time_delay(lastx,lasty,lastz,car)
        car = limit_maximum_value(car)
        car = reverse_or_not(car)
        coords = change_to_hex(car)
        car[4].write([0xFF,0xFE,0x01, coords[0] , coords[1] , coords[2] , coords[3] , coords[4] , coords[5] , car[3] ])
        car[5] = car[5] + 1
        record_position(car)

        processflag = processflag + 1
        #print(processflag)
        time.sleep(time_delay)

    return car


####################################################
#                Some background function
####################################################

# This function estimate the total time needed for car to move to target position 
# The method is "displacement / 4600" , 4600 can be changed depends on situation
# Input argument : x -  coordinate x of target position 
#                  y -  coordinate y of target position
#                  z -  coordinate z of target position
# Output argument : time_delay - the time needed to move to target position
def calculate_time_delay(x,y,z,car = [0,0,0]):

    displacement = ( (x-car[0])**2 + (y-car[1])**2 + (z-car[2])**2 )**0.5
    time_delay = displacement/4600
    if time_delay <= 0.006:
        time_delay = 0.006
    return time_delay


# Send position command through serial to STM32 
# Input argument : car 
# Output argument : car
def move_to_coordinate(car):

    car = limit_maximum_value(car)    # Limit maximum value
    car = reverse_or_not(car)         # Set direction byte
    coords = change_to_hex(car)       # Change number of x,y,z into hex
    #print("{} {} {}".format(car[0],car[1],car[2]))
    #print(" {} {} {} {} {} {} {} {}".format(coords[0],coords[1],coords[2],coords[3],coords[4],coords[5],coords[6],coords[7]))
    car[4].write([0xFF,0xFE,0x01, coords[0] , coords[1] , coords[2] , coords[3] , coords[4] , coords[5] , car[3] , coords[6] , coords[7] ])
    car[5] = car[5] + 1  # car[5] represent number of command sent by this function.
    record_position(car) # Record the command input
    #time.sleep(0.01)
    return car

# Used in accelerate mode ( See set_target_position )
# This function calculate the total encoder needed for car to move from initial velocity to max velocity (Encoder)
# Input argument : acc_time - time for acceleration (s)
#                  max_step - max speed(Encoder)
#                  ini_step - initial speed
# Output argument : displacement - encoder
def acc_calculate_total_displacement(acc_time = 1 , max_step = 32 , ini_step = 0):
    step = 0
    displacement = 0
    time_delay = 0.006
    total_cycle = acc_time/time_delay
    parts = total_cycle / max_step
    if parts < 1:
        acc_rate = 1/parts
        mini_cycle = 0
        for i in range(int(max_step/acc_rate)):
            step = int(ini_step + acc_rate*(i+1))
            displacement = int(displacement + step)
        return displacement

    else:
        acc_rate = 1
        mini_cycle = int(total_cycle/max_step)
        for i in range(max_step-1):
            for j in range(mini_cycle):
                step = int(ini_step + acc_rate*(i+1))
                displacement = displacement + step
        return displacement    


# This is the accelerate method , by increcing the step when starting
# Input argument : car 
#                 angle - the vector angle of target
#                 acc_time - time needed for acceleration
#                 max_step - max speed
#                 ini_step - initial speed
# Output argument : car
def acc_by_time(car,angle,acc_time = 1 , max_step = 32 , ini_step = 0):
    total_cycle = acc_time/0.006 # the loop number of accelerate process
    displacement = 0 # use for debug , represent the total displacement
    step = 0 # use for debug , represent the real time step

    parts = total_cycle / max_step # This variable relate to the amout of loop needed to accelerate to max speed
                                   # if parts < 1 means the loop number aquired to make max_step is larger than 
                                   # total loop needed (since the accelerate rate is 1 ). This will cause problem 

    if parts < 1:
        acc_rate = 1/parts
        mini_cycle = 0
        loop = 0
        for i in range(int(max_step/acc_rate)):
            step = int(ini_step + acc_rate*(i+1))
            displacement = int(displacement + step)
            deltaX = int(round(step*math.cos(angle),0))
            deltaY = int(round(step*math.sin(angle),0))
            car[0] = car[0] + deltaX
            car[1] = car[1] + deltaY
            car = move_to_coordinate(car)
            #print('{}  {}'.format(step,displacement))

            time.sleep(0.006)

    else:
        acc_rate = 1
        mini_cycle = int(total_cycle/max_step)

        for i in range(max_step-1):
            for j in range(mini_cycle):
                step = int(ini_step + acc_rate*(i+1))
                displacement = displacement + step
                deltaX = int(round(step*math.cos(angle),0))
                deltaY = int(round(step*math.sin(angle),0))
                car[0] = car[0] + deltaX
                car[1] = car[1] + deltaY
                car = move_to_coordinate(car)
                #print('{}  {}'.format(step,displacement))
                time.sleep(0.006)

    return car


# This function is unfinished , the goal is combine with lidar evasion
def acc_by_time_lidar(car,sock,angle,acc_time = 1 , max_step = 32 , ini_step = 0):
    total_cycle = acc_time/0.006 # the loop number of accelerate process
    displacement = 0 # use for debug , represent the total displacement
    step = 0 # use for debug , represent the real time step

    parts = total_cycle / max_step # This variable relate to the amout of loop needed to accelerate to max speed
                                   # if parts < 1 means the loop number aquired to make max_step is larger than 
                                   # total loop needed (since the accelerate rate is 1 ). This will cause problem 

    if parts < 1:
        acc_rate = 1/parts
        mini_cycle = 0
        loop = 0
        for i in range(int(max_step/acc_rate)):
            step = int(ini_step + acc_rate*(i+1))
            displacement = int(displacement + step)
            deltaX = int(round(step*math.cos(angle),0))
            deltaY = int(round(step*math.sin(angle),0))
            car[0] = car[0] + deltaX
            car[1] = car[1] + deltaY
            car = move_to_coordinate(car)
            #print('{}  {}'.format(step,displacement))

            time.sleep(0.006)

    else:
        acc_rate = 1
        mini_cycle = int(total_cycle/max_step)

        for i in range(max_step-1):
            for j in range(mini_cycle):
                step = int(ini_step + acc_rate*(i+1))
                displacement = displacement + step
                deltaX = int(round(step*math.cos(angle),0))
                deltaY = int(round(step*math.sin(angle),0))
                car[0] = car[0] + deltaX
                car[1] = car[1] + deltaY
                car = move_to_coordinate(car)
                #print('{}  {}'.format(step,displacement))
                time.sleep(0.006)

    return car


# This function is just the oppsite of acc_by time
def deacc_by_time(car,angle,acc_time = 1 , max_step = 32 , ini_step = 0):
    total_cycle = acc_time/0.006 # the loop number of accelerate process
    displacement = 0 # use for debug , represent the total displacement
    step = 0 # use for debug , represent the real time step

    parts = total_cycle / max_step # This variable relate to the amout of loop needed to accelerate to max speed
                                   # if parts < 1 means the loop number aquired to make max_step is larger than 
                                   # total loop needed (since the accelerate rate is 1 ). This will cause problem 

    if parts < 1:
        acc_rate = 1/parts
        mini_cycle = 0
        loop = 0
        for i in range(int(max_step/acc_rate)):
            step = int(max_step - acc_rate*(i+1))
            displacement = int(displacement + step)
            deltaX = int(round(step*math.cos(angle),0))
            deltaY = int(round(step*math.sin(angle),0))
            car[0] = car[0] + deltaX
            car[1] = car[1] + deltaY
            car = move_to_coordinate(car)
            #print('{}  {}'.format(step,displacement))

            time.sleep(0.006)

    else:
        acc_rate = 1
        mini_cycle = int(total_cycle/max_step)

        for i in range(max_step-1):
            for j in range(mini_cycle):
                step = int(max_step - acc_rate*(i+1))
                displacement = displacement + step
                deltaX = int(round(step*math.cos(angle),0))
                deltaY = int(round(step*math.sin(angle),0))
                car[0] = car[0] + deltaX
                car[1] = car[1] + deltaY
                car = move_to_coordinate(car)
                #print('{}  {}'.format(step,displacement))
                time.sleep(0.006)

    return car

# determine the angle of moving vector
# Input argument : dx - the delta x of target position
#                  dy - the delta y of target position
# Output argument : angle - the vector angle
def vector_angle(dx,dy):
    if dx == 0 and dy > 0 :
        angle = math.radians(90)
        print(1)
    elif dx == 0 and dy < 0 :
        angle = math.radians(270)
        print(2)
    elif dx > 0 and dy == 0:
        angle = math.radians(0)
        print(3)
    elif dx < 0 and dy == 0:
        angle = math.radians(180)
        print(4)
    elif dx == 0 and dy == 0:
        angle = math.radians(0)
        print(5)
    else:
        angle = math.atan2(dy,dx)

    return angle


# Determinte if the command should add the reverse flag (the 10th byte)
# Input argument - car
# Output argument - car
def reverse_or_not (car):
        #Direction X
    if car[0] < 0:
        xrev = 1

    if car[0] >= 0:
        xrev = 0

    #Direction Y
    if car[1] < 0:
        yrev = 1

    if car[1] >= 0:
        yrev = 0

    #Direction Z
    if car[2] < 0:
        zrev = 1

    if car[2] >= 0:
        zrev = 0

    car[3] = int('00000{}{}{}'.format(xrev,yrev,zrev))
    return car

# Record the position command to a recording file .  
# Input argument : car
# No output argument
def record_position(car):
    # Check if file exist
    try:
        f = open('last_position_input.txt','r+')
    except FileNotFoundError:
        f = open('last_position_input.txt','w')
        f.close()
        f = open('last_position_input.txt','r+')

    try:
        fhis = open('history_position_input.txt','a')
    except FileNotFoundError:
        fhis = open('history_position_input.txt','w')
        fhis.close()
        fhis = open('history_position_input.txt','a')        

    #f.write('X:'+str(car[0])+'_Y:'+str(car[1])+'_Z:'+str(car[2]))
    f.write(' X '+str(car[0])+' Y '+str(car[1])+' Z '+str(car[2]))
    fhis.write(str(car[5])+' X '+str(car[0])+' Y '+str(car[1])+' Z '+str(car[2])+' E\n')

# Change decimal to hex , the max number input is 256*256*256 = 16777216 - 1
# Input argument : car
# Output argument : xh - the higher byte of x
#                   xl - the lowest byte of x
#                   xhh - the highest byte of x
def change_to_hex(car):
    xhh = int(abs(car[0])/65536)
    xh = int((abs(car[0])%65536)/256)
    xl = int((abs(car[0])%65536)%256)
    yhh = int(abs(car[1])/65536)
    yh = int((abs(car[1])%65536)/256)
    yl = int((abs(car[1])%65536)%256)
    zh = int(abs(car[2])/256)
    zl = (abs(car[2])%256)

    return xh,xl,yh,yl,zh,zl,xhh,yhh


# Limit the max value of ordered X,Y,Z position ( max = 16777215 )
# Input argument : car
# Output argument : car
def limit_maximum_value(car): 
    if car[0] >= 16777215:
        car[0] = 16777215
    if car[0] <= -16777215:
        car[0] = -16777215

    if car[1] >= 16777215:
        car[1] = 16777215
    if car[1] <= -16777215:
        car[1] = -16777215

    if car[2] >= 16777215:
        car[2] = 16777215
    if car[2] <= -16777215:
        car[2] = -16777215
    return car

# This function is mainly used with xbox control method
# Input argument : car
#                   a - if a is on , increase step by 1
#                   b - if a is on , decrease step by 1
#                  max_step - in position mode , the max step should below 32 . While in velocity mode it can be 131
# Output argument : car
def acc_or_not(car,a,b,max_step = 32):
    if a == 0:
        pass
    if b == 0:
        pass
    if a == 1:
        if car[6] <= max_step:
            car[6] = car[6] + 1
            print('+ {}'.format(car[6]))
            #tcnl.clear()
            tcnl.lcd_string("+ {}".format(car[6]),1)
            #time.sleep(0.1)
    if b == 1:
        if car[6] > 0:
            car[6] = car[6] - 1
            print('+ {}'.format(car[6]))
            #tcnl.clear()
            tcnl.lcd_string("+ {}".format(car[6]),1)
            #time.sleep(0.1)
    return car


#####################################################
#                    Test Function
#___  __  __  ___      __            __ ___ ___  __
# |  |__ |__   |      |__ |  | |\ | |    |   |  |  | |\ |
# |  |__  __|  |      |   |__| | \| |__  |  _|_ |__| | \|


# This is a test function of the one below (lidar_evade_main) , work with TCN_rplidar.evade_8_division_main()
# You can use this one to debug

def lidar_test_main(step = 500, port = '/dev/ttyUSB1'):

    car = init(port)
    sock = tcns.init_server_udp()
    server_retry = 1
    run = True
    while run == True:
        #print(run)
        command = tcns.listen_udp(sock,11)
        print(command)
        if command != None:
            command = command.decode('utf-8')

            #if command != 'None0000000':
            car =lidar_evade(car,command,0,step)
            #else:
                #pass
        else:
            time.sleep(0.006)

def lidar_test_main2(step = 200, port = '/dev/ttyUSB1'):

    car = init(port)
    server_retry = 1
    run = True
    while run == True:
        #print(run)
        y = int(input('enter y'))
        car = set_target_position_adding_lidar(car , 0 ,y ,0,300)
        


# This function is a very basic for "obstacle avoidance" 
# Which is design only for "TCN_rplidar.evade_8_division_main()" . Or any program that output data through socket -$
# with formation "D0000A0000N" ,encode with 'utf-8'(0000 is a 4-byte-string that represent number ) . The first 0000 is distance
# to the obstacle (which is currently no use for this function) and the last 0000 is angle.
# Funtion wil will decode it to number automaticly .
#
# #Example:
# import TCN_position
# lidar_evade_main()

def lidar_evade_main(step = 200, port = '/dev/ttyUSB1'):

    car = init(port)
    sock = tcns.init_server_udp(False)
    server_retry = 1
    run = True
    while run == True:
        try:
            #print(run)
            command = tcns.listen_udp(sock,11)
            print(command)
            if command != None:
                command = command.decode('utf-8')
                car =lidar_evade(car,command,0,step)

        except KeyboardInterrupt:
            run = False
            print('KeyboardInterrupt >>> stop')

        except socket.error:
            print('Server error . Restarting UDP server in 1 second . Retry {}'.format(server_retry))
            if server_retry <= 10:
                time.sleep(1)                
                sock = tcns.init_server_udp()
                server_retry = server_retry + 1
            else:
                print("Retry limitation reached . There may have some problem system can't fix by itself .")
                print("Please check TCN_server")
                run = False

        except :
            print('Fatal error occered , please use lidar_test_main to debug')
            run = False 



def loop_goto_pos_main(port = '/dev/ttyUSB1'):

    car = tcn.init(port)
    while True:
        x = int(input('enter x'))
        y = int(input('enter y'))
        z = int(input('enter z'))
        car = tcn.set_target_position(car,x,y,z)



if __name__ == '__main__':
    #lidar_evade_main()
    lidar_test_main()
    #lidar_test_main2()

            
