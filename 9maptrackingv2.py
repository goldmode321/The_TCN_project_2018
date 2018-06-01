#!/usr/bin/python
# -*- coding: UTF-8 -*-

import TCN_position as tcnp 
import TCN_xbox_velocity as tcnx
import TCN_gpio as tcng
import xbox
import sys, time, xmlrpclib,readline
import math

def main():

    global proxy

    try:
        proxy =  xmlrpclib.ServerProxy("http://192.168.5.100:8080") 
        alive_resp = proxy.alive() #check rpc sever is up
        tcng.init()
        #joy = xbox.Joystick()
    except xmlrpclib.Fault as err:
        print("A fault occurred")
        print(err.faultCode)
        print(err.faultString)
        return 1
    #except IOError as e:
        #print(e)
        #print('retry in 1 second or use KeyboardInterrupt to halt')
        #time.sleep(1)
        #main()
    except:
        print("# Server is not alive")
        print("")
        return 1

    manual_mode(proxy)
    #manual_mode(proxy,joy)


def manual_mode(proxy):
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
                scenario1(proxy)
            
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
                    
                    print(mapids)
                    
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

            

            elif cmd == 'cr':
                try:
                    start_resp = proxy.set_start(0,[int(cmd_list[1])])
                    print( 'Proxy.set_start(), response: {}'.format(start_resp) )
                    #print([int(cmd_list[1])])
                    if str(start_resp).find('Error') == -1:
                        scenario2(proxy)
                except Exception as e:
                    print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
                    print(e)

            

            elif cmd == 'tr':
                try:
                    start_resp = proxy.set_start(0,[int(cmd_list[1])])
                    print( 'Proxy.set_start(), response: {}'.format(start_resp) )
                    #print([int(cmd_list[1])])
                    if str(start_resp).find('Error') == -1:
                        set_target(proxy)
                except Exception as e:
                    print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
                    print(e)


            elif cmd == 'gpio':
                try:
                    joy = xbox.Joystick()
                    print('push rightTrigger')
                    onflag = 1
                    gpioflag = True
                    while gpioflag:
                        if joy.rightTrigger() and onflag == 1:
                            tcng.relay_on()
                            onflag = -onflag
                            print('on')
                            time.sleep(0.2)
                        if joy.rightTrigger() and onflag == -1:
                            tcng.relay_off()
                            onflag = -onflag
                            print('off')
                            time.sleep(0.2)
                        if joy.Back():
                            tcng.relay_off()
                            gpioflag = False
                            print('Back to command mode')
                except IOError as e:
                    print(e)
                    tcng.relay_off()
                    print('Please retry again')
                except KeyboardInterrupt:
                    print('Back to command mode')
                    tcng.relay_off()
                    joy.close()


            elif cmd == 'pr':
                try:
                    start_resp = proxy.set_start(0,[int(cmd_list[1])])
                    print( 'Proxy.set_start(), response: {}'.format(start_resp) )
                    #print([int(cmd_list[1])])
                    if str(start_resp).find('Error') == -1:
                        the_error(proxy)
                except Exception as e:
                    print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
                    print(e)
                


            else:
                print( 'Unknown command, please type help.' )
        except xmlrpclib.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)
            joy.close()
        except KeyboardInterrupt:
            print('Quit by KeyboardInterrupt')
            joy.close()

        except Exception as e:
            print(e)
            joy.close()
            print("# Command error: please check your format or check if server is not alive.")     
            print("  You can type gs to check slam's status.")  

    return




def scenario1(proxy):
    car = tcnp.init()
    print('car')
    try:
        joy = xbox.Joystick()
        print('joy')
        joy.connected()
        print(joy)
    except Exception as e:
        print(e)

    mapping_flag = True
    msgb=""
    while mapping_flag:
        try:
            #print('try')
            tcnx.xbox_velocity_vision(joy,car)
            #print('xbox')
            #time.sleep(0.1)
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
            if joy.Back():
                mapping_flag = False
                print(joy.Back())
                joy.close()
                tcng.relay_off()


        except KeyboardInterrupt:
            joy.close()
            tcng.relay_off()
            #print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
            break
        except Exception as e:
            tcng.relay_off
            joy.close()
            print(e)

def scenario2(proxy):
    joy = xbox.Joystick()
    car = tcnp.init('/dev/ttyUSB1')
    mainflag = True
    while mainflag:
        try:
            runflag = True
            runflagx = True
            runflagy = True
            while runflagx:
                try:
                    tx = int(raw_input('Target X'))
                    runflagx = False
                except KeyboardInterrupt:
                    runflagy = False
                    runflag = False
                    mainflag = False
                    tcng.relay_off()
                    print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
                    break
                except ValueError:
                    print('You must enter numbers')
                except Exception as e:
                    print(e)
                    tcng.relay_off()

                    

            while runflagy:
                try:
                    ty = int(raw_input('Target Y'))
                    runflagy = False
                except KeyboardInterrupt:
                    runflag = False
                    mainflag = False
                    tcng.relay_off()
                    print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
                    break
                except ValueError:
                    print('You must enter numbers')
                except Exception as e:
                    print(e)
                    tcng.relay_off()

            vision_to_target_position(car,joy,tx,ty)

        except KeyboardInterrupt:
            car[0] = 0
            car[1] = 0
            car[2] = 0
            mainflag = False
            tcnp.move_to_coordinate(car)
            tcng.relay_off()
            print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
            break  

        except Exception as e:
            mainflag = False
            print(e)   
            tcng.relay_off()
            print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )

def set_target(proxy):
    try:
        joy = xbox.Joystick()
    except IOError as ioe:
        print(ioe)
        print('reconnect to xbox in 1 second')
        time.sleep(1)
        joy = xbox.Joystick()
    car = tcnp.init('/dev/ttyUSB1')
    msgb=""
    recorded_position = []



    try:
        while True:

            forflag = True
       
            msgb = show_info(proxy,msgb) # Show camera information . show_ifo return msgb . We put msgb back to show info to make it show new data only ( Old data won't be printed)

            tcnx.xbox_velocity_vision(joy,car) # Turn on XBOX control mode

            pose_resp = proxy.get_pose()

            # The behavier when push button 'x'
            if joy.X():
                print('Add new way point')
                car[0] = 0 # Make car stop
                car[1] = 0
                car[2] = 0
                tcnp.move_to_coordinate(car)                
                time.sleep(0.5)
                recorded_position.append([pose_resp[2],pose_resp[3]]) # Remove the last element of recorded_position
                print(recorded_position)
                time.sleep(0.1)
                
            # The behavier when push button 'y'
            if joy.Y():
                print('Delet last generated way point')
                car[0] = 0 # Make car stop
                car[1] = 0
                car[2] = 0
                tcnp.move_to_coordinate(car)
                time.sleep(0.5)
                recorded_position.pop(len(recorded_position) - 1) # Remove the last element of recorded_position
                print(recorded_position)
                time.sleep(0.1)

            # The behavier when push button 'start'
            if joy.Start():
                if len(recorded_position) != 0: # If no position was recorded , then pass
                    for i in range(len(recorded_position)): 
                        position = recorded_position[i]
                        print('Target X : {} Y : {} '.format(position[0],position[1]))
                        forflag =  vision_to_target_position(car,joy,position[0],position[1]) # Move to target according to the camera
                        time.sleep(1)
                        if forflag == False:
                            break
                    recorded_position = [] # Wipe out recording file after execution
                else:
                    print('no recorded position')

            # The behavier when push button 'Back'
            if joy.Back():
                joy.close() # Kill xbox process 
                tcng.relay_off() # Make GPIO pin 4 off
                print('Closing tr mode')
                print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) ) 
                break




    except KeyboardInterrupt:
        tcng.relay_off()
        joy.close()
        print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
    except Exception as e:
        tcng.relay_off()
        print(e)   
        joy.close()
        print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )


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
    print("cr: control coordinate mode.")
    print("tr: tracking mode")
    print("gpio:test if relay alive")
    print("pr:keep moving at 2 position")
    return


#step = 20 ,turn_step = 2 ,error_range = 3 ,deacc_range = 150
def vision_to_target_position(car,joy,tx,ty,angle=0,  step = 15 ,turn_step = 2 ,error_range = 15 ,deacc_range = 150,msgb = ""):
    runflag = True 
    i = 0
    j = 0
    while runflag:

        pose_resp = proxy.get_pose()
        status_resp = proxy.get_status()
        x = pose_resp[2]
        y = pose_resp[3]   
        angle = pose_resp[4]                      
        dx = tx - x
        dy = ty - y
        vxy = move_to_coordinate_speed(dx,dy,angle,step,error_range,deacc_range)

        #if angle > 0:
        #    car[2] =  turn_step
        #if angle < 0:
        #    car[2] = - turn_step

        show_mesflag = True
        str2 = ""


        #while status_resp[0] != 4 : # switch to xbox control
        while pose_resp[5] != 100:

            if show_mesflag == True:
                print('The device cannot identify its current location \n Switch to XBOX_control mode')
                show_mesflag = False


            tcnx.xbox_velocity_vision(joy,car)
            status_resp = proxy.get_status()
            pose_resp = proxy.get_pose()
            str1 = 'con: '+format(pose_resp[5]) + ' status: ' + format(status_resp)

            if str1 != str2:
                print(str1)
                str2 = str1

            if joy.Back():
                runflag = False
                print('Cancel operation')
                time.sleep(1)
                print("Back to 'tr' mode ")
                return False


        # Auto mode
        car[0] = vxy[0]
        car[1] = vxy[1]
        tcnp.move_to_coordinate(car)

        msg1 = "status:" + format(status_resp[0]) + ", "
        msg2 = "mapid:" + format(pose_resp[1]) + ", "
        msg3 = "(x,y):(" + format(pose_resp[2]) + "," + format(pose_resp[3]) + "), "
        msg4 = "thida: " + format(pose_resp[4]) + ", " 
        msg5 = "conf: " + format(pose_resp[5]) 
        msg6 = " ############################### "
        if status_resp[0]==5:
            msga = msg1 + msg2 + msg3 + msg4 + msg5 + msg6
        else:
            msga = msg1 + msg2 + msg3 + msg4 + msg5 +' dx '+str(dx) + ' dy ' + str(dy) + ' vx ' + str(vxy[0]) + ' vy '+ str(vxy[1]) 

        if msgb!=msga:
            print(msga)
            msgb=msga
        # else:
            # print(msga)

        if vxy[0] == 0 and vxy[1] == 0:
            print('Target reached')
            break

        if joy.Back():
            print('Cancel operation')
            car[0] = 0
            car[1] = 0
            car[2] = 0
            tcnp.move_to_coordinate(car)
            time.sleep(1)
            print("Back to setting mode ")
            return False

def show_info(proxy,msgb = ""):
    
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
    return msgb

# This function adjusts the speed when moving to target .
# Input argument : dx - the delta x to target ( dx = target_x - map_x )
#                  dy - the delta y to target ( dy = target_y - map_y )
#                  step
#                  error_range
#                  deacc_range - when car's position is whinin deacc_range , adjust speed depends on distance
# Output argument : vx,vy - velocity of x,y
def move_to_coordinate_speed(dx,dy,angle,step,error_range,deacc_range):
        
        angle = (math.degrees(math.atan2(dy,dx))%360+angle)%360
        print(round(angle,2))

        dis = ( dx**2 + dy**2 )**0.5

        if error_range < abs(dis) :
            if abs(dis) < deacc_range:
                vx = step * dis/deacc_range * math.cos(math.radians(angle))
                vy = step * dis/deacc_range * math.sin(math.radians(angle))
                if 0 <= vx < 1 :
                    vx = 1
                elif -1 < vx < 0 :
                    vx = -1
                if 0 <= vy < 1 :
                    vy = 1
                elif -1 < vy < 0 :
                    vy = -1

                time.sleep(0.01)
            else:
                vx = step* math.cos(math.radians(angle))
                vy = step* math.sin(math.radians(angle))
                
        else:
            vx = 0
            vy = 0


        return vx,vy

def the_error(proxy):
    try:
        joy = xbox.Joystick()    
    except IOError as e:
        print(e)
        print('Try reconnecting in 1 second')
        joy =xbox.Joystick()

    car = tcnp.init('/dev/ttyUSB1')
    mainflag = True
    recorded_position = []
    msgb = ""
    print('Please locate 2 position')


    while mainflag:
        try:
            innerflag = True
            pose_resp = proxy.get_pose()
            tcnx.xbox_velocity_vision(joy,car)
            msgb = show_info(proxy,msgb)

            # The behavier when push button 'x'
            if joy.X():
                print('Add new way point')
                car[0] = 0 # Make car stop
                car[1] = 0
                car[2] = 0
                tcnp.move_to_coordinate(car)                
                time.sleep(0.5)
                recorded_position.append([pose_resp[2],pose_resp[3]]) # Remove the last element of recorded_position
                print(recorded_position)
                time.sleep(0.1)
                
            # The behavier when push button 'y'
            if joy.Y():
                print('Delet last generated way point')
                car[0] = 0 # Make car stop
                car[1] = 0
                car[2] = 0
                tcnp.move_to_coordinate(car)
                time.sleep(0.5)
                recorded_position.pop(len(recorded_position) - 1) # Remove the last element of recorded_position
                print(recorded_position)
                time.sleep(0.1)



            if joy.Start():
  
                while innerflag:
                    for i in range(len(recorded_position)): 
                        position = recorded_position[i]
                        print('Target X : {} Y : {} '.format(position[0],position[1]))
                        forflag =  vision_to_target_position(car,joy,position[0],position[1]) # Move to target according to the camera
                        time.sleep(1)

                        if forflag == False:
                            innerflag = False
                            recorded_position = []
                            break

                    if forflag != False:
                        for j in range(len(recorded_position)): 
                            position = recorded_position[len(recorded_position)-1-j ]
                            print('Target X : {} Y : {} '.format(position[0],position[1]))
                            forflag =  vision_to_target_position(car,joy,position[0],position[1]) # Move to target according to the camera
                            time.sleep(1)

                            if forflag == False:
                                innerflag = False 
                                recorded_position = []                               
                                break

                    if joy.Back():
                        innerflag = False
                        print('Back to setting mode')
                        time.sleep(1)

                recorded_position = []
                print('Please set  position')



            if joy.Back():
                mainflag = False
                print('Back to command mode')
                tcng.relay_off()
                print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )



        except KeyboardInterrupt:
            car[0] = 0
            car[1] = 0
            car[2] = 0
            mainflag = False
            tcnp.move_to_coordinate(car)
            tcng.relay_off()
            print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )
            break  

        except Exception as e:
            mainflag = False
            print(e)   
            tcng.relay_off()
            print( 'Proxy.set_reset(), response: {}'.format(proxy.set_reset()) )




if __name__ == "__main__":
    sys.exit(main())
