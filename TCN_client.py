import socket
import time
import os
import sys

# This function setup UDP client 
# Input arguments : ip,port - the address of socket server
# Output arguments : sock - the socket object that create
#                    address - (ip,port)
def init_client_udp(ip = '127.0.0.1',port = 50003):

    address =(ip,port)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return sock,address

    except:
        sock.close()
        time.sleep(0.1)
        print('restarting client')
        time.sleep(0.1)
        init_client_udp()

# This one send encoded data to server 
# Input arguments : sock - the object represent socket tunnel.
#                   address - represent IP:Port
# No output value . 
def send_udp(sock,address,message):
    try:
        message = message.encode('utf-8') # Encode message before send . 
        sent = sock.sendto(message,address ) # Send message ( I forgot what's the return value of sendto() )

    except Exception as e: # If error happen , show error and unbind socket. 
        print(e)
        sock.close()


#=============Example Function===============

# Example function
def client_main_udp(message = '0123456789N'):
    data = init_client_udp()
    print('start sending')

    while True:
        send_udp(data[0],data[1],message)
        time.sleep(0.1)