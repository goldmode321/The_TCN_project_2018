#This Package allows you to set socket communication easily.
#Put this package in the same folder with your code, and import it.
#Author : Eric J. Tzeng 2018.03.08

#Example Code Server.py:
#============================================================================

# import TCN_socket

# def main():
# 	ports_list = [50004,50005]
# 	Socket_list= TCN_socket.InitialServer(ports_list)
# 	for i in range(0,10):
# 		data1 = TCN_socket.ServerCommunicate(Socket_list[0],12,0.01,2,'456456456') #mode 2
# 		data2 = TCN_socket.ServerCommunicate(Socket_list[1],12,0.01) #mode 1
# 		print('from client 01 : ' + data1)
# 		print('from client 02 : ' + data2)
# 	TCN_socket.CloseSocket(Socket_list)

# if __name__ == '__main__':
# 	main()

#============================================================================

#Example Code Client01.py:
#============================================================================

# import TCN_socket

# def main():
# 	Sock_Cli = TCN_socket.InitialClient("127.0.0.1", 50004)
# 	for i in range(0,10):
#		data  = TCN_socket.ClientCommunicate(Sock_Cli,'123123123',2,9) #mode 2
# 		print('data receive form server is : ' + data)
# if __name__ == '__main__':
# 	main()

#============================================================================

#Example Code Client02.py:
#============================================================================

# import TCN_socket

# def main():
# 	Sock_Cli = TCN_socket.InitialClient("127.0.0.1", 50005)
# 	for i in range(0,10):
# 		TCN_socket.ClientCommunicate(Sock_Cli,'abcabcabc') # Send only mode 1
# if __name__ == '__main__':
# 	main()

#============================================================================


import socket
import sys
import os
import time


def main():
	pass
	# ports_list = [50000]
	# Sock_list, Con_list = InitialServer(ports_list)
	# for i in range(0,10):
	# 	data = ReceiveMessage_Server(Sock_list[0],Con_list[0],9,0.1)
	# 	print(data)
	# CloseSocket(Sock_list,Con_list)
#Above Code is for maintainece usage

#Function InitialServer(ports_list):
#It will return Socket_list for later usage.
#Depends on your usage, you can initialized multiple connections by setting 
#ports_list with this formate "[port1,port2,port3,port4...]", and I recomm-
#anded your ports starts from 50000(We don't wants to interfer with system 
#used port).Finally, make sure you start Server before Client.

def InitialServer(ports_list = [50000]):
	local_address = '127.0.0.1'
	Soc_list = list()
	count = 0
	for port in ports_list:
		try:
			sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    #Started Socked as standard
			sock.bind((local_address,port))
			sock.listen(1)
			Soc_list.append(sock)
			print('Socket %d is waiting for connection' %(count))
		except:
			sock.close()
			sock.bind((local_address,port))
			sock.listen(1)
			Soc_list.append(sock)
			print('Socket %d is waiting for connection' %(count))
		count +=1
	Con_list = list()
	count = 0
	for Soc in Soc_list:
		connection, Clients_Address = Soc.accept()
		Con_list.append(connection)
		print('Socket %d is Connected' %(count))
		count += 1
	print('All Clients is connected')
	Socket_list = list()
	for i in range(0,len(Soc_list)):                               #Assemble output formate
		Socket_list.append([Soc_list[i],Con_list[i]])
	return Socket_list

#Function ServerCommunicate(Socket_list,Data_Length,time_delay[,Server_mode,message]):
#This Function is for receive data from Client, make sure you input Socket_list
#from InitialServer, it will give client go flag to start sending message, and 
#that this function will receive the message and return it. There is some heads
#-up, first your data length must larger than your message Length, or you will 
#receive "wrong data format". Second, the time delay is to control client's me-
#ssage sending frequency. Finally, if tou wants to sends message to client, you
#can set mode = 2, and give input the message you want to send.

def ServerCommunicate(Socket_list,Length,delay = 0.5,mode = 1,message = ''):
	try:
		if mode == 1:
			message = 'next'
		if mode == 2:
			message = 'next-HH' + message + 'EE'    #Send next flag and message which HH...EE Check Value
		Socket_list[1].send(message.encode('utf8'))
		data = Socket_list[1].recv(Length+4)
		data = data.decode('utf-8')
		#print(data)
		#Socket.close()
	except:
		data = 'data error'
		print('No_connection')
	
	if data[0:2]=='HH' and (data[-2]+data[-1])=='EE':   #Check if data is correct
		data = data[2:len(data)-2]
	else:
		data = 'data error'
		print('Wrong Data Format')                  #Data Langth Error

	time.sleep(delay)
	return data




#Function InitialClient(IP_Address,Port)
#Use it after Server is startred, and before you use ClientCommunicate()
#This function will return Socket object


def InitialClient(IP_Address,Port,re_try = 0):
	try:
		Socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		Socket.connect((IP_Address,Port))
		return Socket
	except socket.error:
		try:
			print('Server is not listening')
			if re_try == 1:
				time.sleep(0.5)
				InitialClient(IP_Address,Port,re_try)
		except KeyboardInterrupt:
			sys.exit('exit')




#Function ClientCommunicate(Socket,message[,client_mode,data_length])
#Input Socket Which is generated from InitialClient(), and message you want to send
#. If ServerCommunicate() is set to mode 2, make sure you set the client_mode to 2 
#and input the correct message Length from Server 

def ClientCommunicate(Sock,message,mode = 1,Length = 4):
	data = ''
	message = 'HH' + message + 'EE'
	goflag = 0
	while goflag == 0:
		data = Sock.recv(Length + 9)  #Adding check value length
		data = data.decode('utf-8')
		check = data[0:4]             #First four is check flag
		if mode == 2:
			data = data = data[5:len(data)]
		if check == 'next':
			goflag = 1
		if check == 'stop':
			sys.exit(0)

	try:
		Sock.send(message.encode('utf-8'))
	except BrokenPipeError:
		print('Server lost')

	if mode == 2:
		if data[0:2]=='HH' and (data[-2]+data[-1])=='EE':  #Check if data is correct
			data = data[2:len(data)-2]
		else:
			data = 'data error'
			print('Wrong Data Format')
	return data





#Function CloseSocket(Socket_list)
#Make sure you use it eyerytimes after Server py Script finished, it will
#reset socket. Next time when you use it, it will work properly. 

def CloseSocket(Socket_list):
	for Sock in Socket_list:
		Sock[1].send('stop'.encode('utf8'))                #Send Signal to stop client
	for Sock in Socket_list:
		Sock[0].close()
	print('All Sockets Closed')




if __name__ == '__main__':
	main()