
import socket
import sys
import os
import time


# This function setup the udp link .
#
# Input arguments : IP , port , setblocking : IP - the server ip ; s_port - port that data send ; 
#                   setblocking - if is 0 , the program will raise error if it doesn't recive any message within timeout.
#                                 if is 1 , the program will pause and wait until receive message
#                                 # For this project , there is currently no setting for the time of timeout.
# Output argument : sock - socket object which represent 
def init_server_udp(IP = '127.0.0.1' , s_port = 50003 ,setblocking = 0):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.setblocking(setblocking) # If setblocking = 1 , program will pause until get message sent by client( See listen_udp() )

    try:
        sock.bind((IP,s_port)) # Once binded , the program must have close() to make sure this tunnel won't be occupied by this program
        return sock

    except :
        sock.close() # Make the Socket tunnel unoccupied when error happen , so that you can bind socket to the address successfully next time.
        time.sleep(0.1)
        print('restarting server')
        time.sleep(0.1)
        init_server_udp() # This allow system automaticly redo server establishment.




# This function return the message from socket
# Can be used for TCP , also. 
# Can be used for client , too . If client is the one that receive message .
#
# Input arguments : sock - the object represent socket tunnel.
#                   length - the length of string to get
# Output arguments : data - the data sent by client
def listen_udp(sock,length = 11):
    try:       
        data = sock.recv(length) # recv return the message which is got from client
        return data

    except socket.timeout: # if server didn't get any data in a period of time 
        pass               # Do nothing and pass  , the return data is 'None' 

    except KeyboardInterrupt: 
        sock.close() # Unbind socket from the adress
        sys.exit(0) # Exit program
    except socket.error:
        pass
    except Exception as e:
        print(e)
        sock.close()
        print('got some error, restarting server in 1 second')
        time.sleep(1)
        


        server_main_udp() # This is needed only if you use sever_main_udp as you main *****************************


#=================Example Function========================

# Example function 1
def server_main_udp():
    sock = init_server_udp()

    while True:
        try:
            data = listen_udp(sock)
            if data != None:
                print(data)
            else:
                print(data)

        except KeyboardInterrupt:
            sock.close()
            sys.exit(0)

if __name__ == '__main__':
    server_main_udp()



