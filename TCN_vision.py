# encoding: utf-8

import sys, time, xmlrpclib,readline

def main():

	global proxy

	try:
		proxy =  xmlrpclib.ServerProxy("http://192.168.5.100:8080") 
		alive_resp = proxy.alive() #check rpc sever is up
	except xmlrpclib.Fault as err:
	    print("A fault occurred")
	    print(err.faultCode)
	    print(err.faultString)
	    return 1
	except:
		print("# Server is not alive")
		print("")
		return 1

	manual_mode()


def manual_mode():
	print("# type h to refer command usage.")
	
	while True:
		command = raw_input('command：')
		cmd_list = command.lower().split() #splits the input string on spaces
		cmd = cmd_list[0]
		try:
			if (cmd == 'h') or (cmd == 'help') :
				help_manual()
			elif cmd == 'al':
				alive_resp = proxy.alive()
				print( 'Proxy.alive(), response: {}'.format(alive_resp) )
			elif cmd == 'cc':
				cc_resp = proxy.check_cpu_speed()
				print( 'Proxy.get_att(), response: {}'.format(cc_resp) )					
			elif cmd == 'gp':
				pose_resp = proxy.get_pose()
				print( 'Proxy.get_pose(), response: {}'.format(pose_resp) )
			elif cmd == 'gs':
				status_resp = proxy.get_status()
				print( 'Proxy.get_status(), response: {}'.format(status_resp) )			
			elif cmd == 's1':
				scenario1()
			elif cmd == 'sc1':
				if len(cmd_list)<6:
					print("Error: wrong st arguments, uasge: sc1 <standard> <length1> <length2> <length3>  <length4> ")
				else:
					print( 'Request fp-slam to make 1st correction.' )
					itercmd = iter(cmd_list)
					next(itercmd)
					length_array = [int(ii) for ii in itercmd] 
					start_resp = proxy.set_correct1(length_array)
					print( 'Proxy.set_start(), response: {}'.format(start_resp) )		
			elif cmd == 'sd':
				print( 'Request fp-slam to shutdown.' )
				proxy.system.shutdown("")
			
			elif cmd == 'st':
				if len(cmd_list)<3:
					print("Error: wrong st arguments, uasge: st <mode> <map id> <map id> ... ")
				else:
					smode = int(cmd_list[1])
					itercmd = iter(cmd_list)
					next(itercmd)
					next(itercmd)
					mapids = [int(ii) for ii in itercmd] 
					start_resp = proxy.set_start(smode,mapids)
					print( 'Proxy.set_start(), response: {}'.format(start_resp) )				
			elif cmd == 'sv':
				save_resp = proxy.save_db()
				print( 'Proxy.save_db(), response: {}'.format(save_resp) )
			elif (cmd == 'qi') or (cmd == 'ex'):
				print( 'Quit now.' )
				print("")
				break
			elif (cmd == 'rs'):
				reset_resp = proxy.set_reset()
				print( 'Proxy.set_reset(), response: {}'.format(reset_resp) )
			elif (cmd == 'hasd'):
				reset_resp = proxy.hardware_shutdown()
				print( 'Proxy.hardware_shutdown(), response: {}'.format(reset_resp) )		
			else:
				print( 'Unknown command, please type help.' )
		except xmlrpclib.Fault as err:
		    print("A fault occurred")
		    print("Fault code: %d" % err.faultCode)
		    print("Fault string: %s" % err.faultString)
		except:
			print("# Command error: please check your format or check if server is not alive.")		
			print("  You can type gs to check slam's status.")	

	return




def scenario1():
	msgb=""
	for num in range(0,500):
		time.sleep(0.1)
		pose_resp = proxy.get_pose()
		status_resp = proxy.get_status()
		msg1 = "status:" + format(status_resp[0]) + ", "
		msg2 = "mapid:" + format(pose_resp[1]) + ", "
		msg3 = "(x,y):(" + format(pose_resp[2]) + "," + format(pose_resp[3]) + "), "
		msg4 = "thida: " + format(pose_resp[4]) + ", " 
		msg5 = "conf: " + format(pose_resp[5]) 
		msg6 = " ############################### "
		if status_resp[0]==5:
			msga = msg1 + msg2 + msg3 + msg4 + msg5 + msg6
		else:
			msga = msg1 + msg2 + msg3 + msg4 + msg5

		if msgb!=msga:
			print(msga)
			msgb=msga
		# else:
			# print(msga)
					

def help_manual():
	print("al: chekc fp-slam is alive.")
	print("cc: check cpu speed.")
	print("gp: get pose from fp-slam.")
	print("gs: get state from fp-slam.")
	print("qi: quit client program.")
	print("s1: scenario1")
	print("sc1 <standard> <length1> <length2> <length3>  <length4> : to correct initial corridation.")
	print("rs: reset the fp-slam system. before re-start another system mode.")
	print("sd: shutdown the fp-slam system.")
	print("sn <nfs address> : set nfs address")
	print("st <system mode> <map id> <map id> ....<map id>: set fp-slam to start.")
	print("sv: save database.")
	return

if __name__ == "__main__":
    sys.exit(main())
