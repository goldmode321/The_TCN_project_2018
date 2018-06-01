from rplidar import RPLidar
from rplidar import RPLidarException
import TCN_client as tcnc
import math
import time
import sys
#port = '/dev/ttyUSB0'





# This one sort list x by length , it will also cut any elemet which length(x[0]) is 0
# Input argument : x - the list get from lidar , the content is in the format of [ distance , angle ]
#                 length - In unit 'mm' , all detection which distance is larger than length will be wipe out
#                 lidar - RPLidar object
# Output argument : coords - the command which will be sent by socket in a kind of formation . 
#                            ( See TCN_position - lidar_evade or TCN_velocity - lidar_evade_velocity)
def data_sort_all_dir_closest_object(x,length,lidar):
    try:
        x = sort_data(x,length)
        x = [x for x in x if x != [0,0]] # Wipe out any element that is [0,0]

        if x == None or x == []:
            pass
        else:
            x.sort() # Arrange it from smallest to tallest
            obj = x[0] # Get the smallest one
            coords = turn_into_line_command(obj[0],obj[1])

            return coords
    except KeyboardInterrupt:
        stopping(lidar)

# Turn of RPLidar sensing function
# Input argument : lidar
# No output 
def stopping(lidar):
    print('stoping')
    lidar.stop()
    lidar.disconnect()

# Turn the distance,angle information into the standard format of TCN protocle
# Input argument : distance
#                   angle
# Output argument : command - A string content distance , angle information . For instance "D0100A0005" means there is
#                             an particle at angle 5 distance 100
def turn_into_line_command(distance , angle):
    string = ''
    d = int(round(distance,0))
    a = int(round(angle,0))

    d = 'D'+ make_same_length(str(d))
    a = 'A'+ make_same_length(str(a))

    command = d + a + 'N'
    return command

# To make sure that the commands are in the same length
def make_same_length(string):
    if len(string) == 1:
        string = '000'+ string
    if len(string) == 2:
        string = '00' + string
    if len(string) == 3:
        string = '0' + string
    return string


# Initialize lidar
# Input argument : port - the port address of RPLidar ( Can be found at /dev )
# Output argument : lidar - RPLidar object
def init():
    print('Scanning RPLidar port')
    for i in range(20):
        try:
            port = '/dev/ttyUSB'+str(i)
            print('Scanning '+port)
            lidar = RPLidar(port)
            state = lidar.get_health()
            if state[0] == 'Good':
                print(state)
                return lidar
            else:
                print(state)
                print('1 or more undefined problems ')


        except RPLidarException as re:
            print(re)
            print('Not this one , system continue scanning')
            pass

    #try:
    #    lidar = RPLidar(port)
    #except KeyboardInterrupt:
    #    stopping(lidar)
    #except:
    #    print('lidar error')
    #    time.sleep(0.5)
    #    lidar = RPLidar(port) # Retry if error

    #return lidar

# This function remove any element which distance is larger than length and smaller than 300mm
# Input argument : x - List which all elements in the format of [ distance , angle]
#                 length - the element which distance is larger than length will set as zero (angle included)
# Output argument : x
def sort_data(x,length):
    if length < 460: # the length should not be less than 460
        length = 460
    for i in range(len(x)): 
        #print(x[i][1])     
        if x[i][0] > length:
            x[i] = [0,0]
        if x[i][0] < 300:
            x[i] = [0,0]
    return x

# Divide the detections into 8 zone by angle
# This function haven't finished yet
def data_arrangement_8_division(data):
    data1 = []
    data2 = []
    data3 = []
    data4 = []
    data5 = []
    data6 = []
    data7 = []
    data8 = []

    for i in range(len(data)):

        if 45 > data[i][1] >= 0:
            data1.append(data[i][0])
        if 90 > data[i][1] >= 45:
            data2.append(data[i][0])
        if 135 > data[i][1] >= 90:
            data3.append(data[i][0])
        if 180 > data[i][1] >= 135:
            data4.append(data[i][0])
        if 225 > data[i][1] >= 180:
            data5.append(data[i][0])
        if 270 > data[i][1] >= 225:
            data6.append(data[i][0])
        if 315 > data[i][1] >= 270:
            data7.append(data[i][0])
        if 360 > data[i][1] >= 315:
            data8.append(data[i][0])
    print(data1)
    return data


#===========================================================
#================== Example Function ===========================

def evade_8_division_main(length = 10 , port = '/dev/ttyUSB0'):

    data = []
    print('lowest length is {} cm'.format(length))
    radius = (length + 40)*10 # in mm
    lidar = init(port)
    try:
        for m in lidar.iter_measurments(): 
            data.append([m[3] ,m[2]]) # (distance , angle)   
            if m[0] == 1:
                coords = data_arrangement_8_division(data)
                data.clear()
    except KeyboardInterrupt:
        stopping(lidar)
        sys.exit(0)
    except :
        print('error occer ,restarting lidar')
        time.sleep(1)
        evade_8_division_main(length , port)

# Input argument : length - In unit "cm" ,determine any detection within lenth should be define as obstacle
#                 lidar_port - The address of RPLidar ( can be seen at /dev )
#                   mode - currently no use
def evade_all_dir_main(length = 20 , lidar_port = '/dev/ttyUSB0' , mode = 1):

    x = []
    print('lowest length is {} cm'.format(length))
    radius = (length + 40)*10 

    lidar = init(lidar_port)

    sock = tcnc.init_client_udp()
    #print(socket)
    
    try:
        for m in lidar.iter_measurments(): # Useful way to get sensing data [ new , quality , angle ,distance ] 
            x.append([m[3] ,m[2]])   
            if m[0] == 1:
                if mode == 1:
                    coords = data_sort_all_dir_closest_object(x,radius,lidar)
                    if coords == None:
                        print(coords)
                        #tcnc.send_udp(sock[0],sock[1],'None0000000')
                    if coords != None:
                        print(coords)
                        tcnc.send_udp(sock[0],sock[1],coords)
                    x.clear()



    except KeyboardInterrupt: # When enter Ctrl+C , conduct the code below
        
        stopping(lidar)
#    except:
#        evade_all_dir_main(length)


if __name__ == '__main__':
    #evade_8_division_main()
    evade_all_dir_main()