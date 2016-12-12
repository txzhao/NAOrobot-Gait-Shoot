# -*- encoding: UTF-8 -*-

'''
      娉ㄦ剰锛侊紒锛�
    鎵�鐢ㄥ嚱鏁板弬鑰冪偣鍧囦负璐ㄥ績鎵�鍦ㄧ偣鍝︼紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛�
    涓嶄粩缁嗙湅浼氭鐨勫緢鎯ㄧ殑鍣㈠櫌鍣㈠櫌锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛侊紒锛�
'''

import sys
import time
from naoqi import ALProxy
from math import sin,cos,asin,acos,atan2,sqrt,exp
DT0=5
StandInitSpeed=0.5
# Define Object
ThighLength=100.0
TibiaLength=102.9
# stand init
LegHight=-(ThighLength+TibiaLength)+20
StepHeight=-180.0
UPHeight=20
# height of body heart
z=150.0
# gravity mm.s_1
g=980.0
# half step
XS=40.0
# body heart switch interpolation number
NS=20
# half switch time
TS=0.5
dTS=TS/NS
dXS=XS/NS
# define FS 
FS=sqrt(g/z)
# define gain
Gain=XS/2/(exp(FS*TS)-exp(-FS*TS)) 

# Move_BC
TM=0.5
NM=20
YM=60.0
dTM=TM/NM
dYM=YM/NM
# Names
names=["RHipRoll","RHipPitch","RKneePitch","RAnklePitch","RAnkleRoll","LHipRoll","LHipPitch","LKneePitch","LAnklePitch","LAnkleRoll"]


def Leg_IK(x,y,z):
    angle=[0,0,0,0,0]
    # z=z-ThighLength-TibiaLength
    angle[0]=atan2(y,-z)
    k=z*cos(angle[0])-y*sin(angle[0])
    tmp=x*x+k*k-ThighLength*ThighLength-TibiaLength*TibiaLength
    angle[2]=acos(tmp/(2*TibiaLength*ThighLength))
    m=(x*x+k*k+ThighLength*ThighLength-TibiaLength*TibiaLength)/(2*k)
    a=2*x*m/k;
    tmp=x*x/(k*k)-1
    b=a*a-4*(ThighLength*ThighLength-m*m)*tmp
    c=2*ThighLength*tmp
    d=(a+sqrt(b))/c
    if abs(d)>1:
        d=d=(a-sqrt(b))/c 
    angle[1]=abs(asin(d))
    angle[1]=-angle[1]
    angle[3]=-angle[1]-angle[2]
    angle[4]=-angle[0]
    return angle

#if right>0 right leg not go 
def Move_Leg(motionProxy,right,ori,terminal):
    angleLists=[range(NM) for i in range(len(names)/2)]    
    #timeLists=[[dTM*(i+1) for i in range(NM)] for j in range(len(names)/2)]
    timeLists=[[dTM*(i+DT0) for i in range(NM)] for j in range(len(names)/2)]
    if(right>0):
        y=YM
    else:
        y=-YM
    if (right==0):
        angle0=Leg_IK(ori,y,StepHeight+UPHeight)
        motionProxy.angleInterpolation(names[0:5], angle0, [1,1,1,1,1], True)
    # Move left 
    else:
        angle0=Leg_IK(ori,y,StepHeight+UPHeight)
        motionProxy.angleInterpolation(names[5:10], angle0, [1,1,1,1,1], True)
    dx=(terminal-ori)/NM
    for i in range(NM):
        angle0=Leg_IK(i*dx+ori,y,StepHeight+UPHeight)
        for j in range(len(names)/2):
            angleLists[j][i]=angle0[j]
        
    if (right==0):
        motionProxy.angleInterpolation(names[0:5], angleLists, timeLists, True)
        angle0=Leg_IK(terminal,y,StepHeight)
        motionProxy.angleInterpolation(names[0:5], angle0, [1,1,1,1,1], True)
    # Move left 
    else:
        motionProxy.angleInterpolation(names[5:10], angleLists, timeLists, True)
        angle0=Leg_IK(terminal,y,StepHeight)
        motionProxy.angleInterpolation(names[5:10], angle0, [1,1,1,1,1], True)
    '''
    if right:
        angle0=Leg_IK(ori,YM,StepHeight+UPHeight)
        t=0.2
        motionProxy.angleInterpolation(names[5:10], angle0, [t,t,t,t,t], True)
        angle0=Leg_IK(terminal,YM,StepHeight+UPHeight)
        t=0.5
        motionProxy.angleInterpolation(names[5:10], angle0, [t,t,t,t,t], True)
        angle0=Leg_IK(terminal,YM,StepHeight)
        t=0.2
        motionProxy.angleInterpolation(names[5:10], angle0, [t,t,t,t,t], True)
        
    else:
        angle0=Leg_IK(ori,-YM,StepHeight+UPHeight)
        t=0.2
        motionProxy.angleInterpolation(names[0:5], angle0, [t,t,t,t,t], True)
        angle0=Leg_IK(terminal,-YM,StepHeight+UPHeight)
        t=0.5
        motionProxy.angleInterpolation(names[0:5], angle0, [t,t,t,t,t], True)
        angle0=Leg_IK(terminal,-YM,StepHeight)
        t=0.2
        motionProxy.angleInterpolation(names[0:5], angle0, [t,t,t,t,t], True)
    '''

def Step_Start(motionProxy,right):
    angleLists=[range(NM) for i in range(len(names))]    
    #timeLists=[[dTM*(i+1) for i in range(NM)] for j in range(len(names))]
    timeLists=[[dTM*(i+DT0) for i in range(NM)] for j in range(len(names))]
    
    # Move BC down
    dx=(StepHeight-LegHight)/NM
    for i in range(NM):
        angle0=Leg_IK(0,0,LegHight+dx*(i+1))
        angle=angle0+angle0
        for j in range(len(names)):
            angleLists[j][i]=angle[j]
    motionProxy.angleInterpolation(names, angleLists, timeLists, True)
    
    # Move BC left or right
    for i in range(NM):
        if (right>0):
            angle0=Leg_IK(0,i*dYM,StepHeight)
        else:
            angle0=Leg_IK(0,-i*dYM,StepHeight)
        angle=angle0+angle0
        for j in range(len(names)):
            angleLists[j][i]=angle[j]
    motionProxy.angleInterpolation(names, angleLists, timeLists, True)
    
    # Move leg out step/2
    Move_Leg(motionProxy,right,0,XS)
    
def Step_Stop(motionProxy,right):
    # half the switch step
    angleLists=[range(NM) for i in range(len(names))]    
    #timeLists=[[dTM*(i+1) for i in range(NM)] for j in range(len(names))]
    timeLists=[[dTM*(i+DT0) for i in range(NM)] for j in range(len(names))]
    #Step_Switch(motionProxy,right)
    # Move leg out step/2
    Move_Leg(motionProxy,right,-XS,0) 
    # Move BC left or right
    for i in range(NM):
        if (right>0):
            angle0=Leg_IK(0,YM-i*dYM,StepHeight)
        else:
            angle0=Leg_IK(0,-YM+i*dYM,StepHeight)
        angle=angle0+angle0
        for j in range(len(names)):
            angleLists[j][i]=angle[j]
    motionProxy.angleInterpolation(names, angleLists, timeLists, True)
    

def Step_Switch(motionProxy,right):
    # half the switch step
    angleLists=[range(2*NS) for i in range(len(names))]    
    #timeLists=[[dTS*(i+1) for i in range(2*NS)] for j in range(len(names))]
    timeLists=[[dTS*(i+DT0) for i in range(2*NS)] for j in range(len(names))]
    if(right>0):
        for i in range(NS):
            #tmp=exp(FS*(TS-i*dTS))
            #dx=Gain*(tmp-1/tmp)
            dx=1.0/2*(i/float(NS))*(i/float(NS))
            angle0=Leg_IK(-XS*dx,YM-dx*2*YM,StepHeight)
            angle1=Leg_IK(XS-XS*dx,YM-dx*2*YM,StepHeight)
            angle=angle0+angle1
            for j in range(len(names)):
                angleLists[j][i]=angle[j]
        for i in range(NS):
            #tmp=exp(FS*i*dTS)
            #dx=Gain*(tmp-1/tmp)
            dx=1-1.0/2*(1-i/float(NS))*(1-i/float(NS))
            angle0=Leg_IK(-XS*dx,YM-dx*2*YM,StepHeight)
            angle1=Leg_IK(XS-XS*dx,YM-dx*2*YM,StepHeight)
            angle=angle0+angle1
            for j in range(len(names)):
                angleLists[j][NS+i]=angle[j]
    else:
        for i in range(NS):
            #tmp=exp(FS*(TS-i*dTS))
            #dx=Gain*(tmp-1/tmp)
            dx=1.0/2*(i/float(NS))*(i/float(NS))
            angle0=Leg_IK(-XS*dx,-YM+dx*2*YM,StepHeight)
            angle1=Leg_IK(XS-XS*dx,-YM+dx*2*YM,StepHeight)
            angle=angle1+angle0
            for j in range(len(names)):
                angleLists[j][i]=angle[j]
        for i in range(NS):
            #tmp=exp(FS*i*dTS)
            #dx=Gain*(tmp-1/tmp)
            dx=1-1.0/2*(1-i/float(NS))*(1-i/float(NS))
            angle0=Leg_IK(-XS*dx,-YM+dx*2*YM,StepHeight)
            angle1=Leg_IK(XS-XS*dx,-YM+dx*2*YM,StepHeight)
            angle=angle1+angle0
            for j in range(len(names)):
                angleLists[j][NS+i]=angle[j]
    motionProxy.angleInterpolation(names, angleLists, timeLists, True)   
  
def Step_One(motionProxy,postureProxy,times):
    right=1
    left=0
    postureProxy.goToPosture("StandInit", StandInitSpeed)
    Step_Start(motionProxy,right)
    #Move_Leg(motionProxy,right)
    #Move_CenterCenter(motionProxy)
    # BC move to left
    Step_Switch(motionProxy,right)
    Move_Leg(motionProxy,left,-XS,XS)
    Step_Switch(motionProxy,left)
    for i in range(times-1):
        Move_Leg(motionProxy,right,-XS,XS)
        Step_Switch(motionProxy,right)
        Move_Leg(motionProxy,left,-XS,XS)
        Step_Switch(motionProxy,left)
    Step_Stop(motionProxy,right)
    
def TI(motionProxy,postureProxy,right,Length,ts):
    angleLists=[range(NM) for i in range(len(names))]    
    #timeLists=[[dTM*(i+1) for i in range(NM)] for j in range(len(names))]
    timeLists=[[dTM*(i+DT0) for i in range(NM)] for j in range(len(names))]
    postureProxy.goToPosture("StandInit", 0.3)
    '''# Move BC down
    StepHeight=-170
    dx=(StepHeight-LegHight)/NM
    for i in range(NM):
        angle0=Leg_IK(0,0,LegHight+dx*(i+1))
        angle=angle0+angle0
        for j in range(len(names)):
            angleLists[j][i]=angle[j]
    motionProxy.angleInterpolation(names, angleLists, timeLists, True)
    
    # Move BC left or right
    for i in range(NM):
        if (right>0):
            angle0=Leg_IK(0,i*dYM,StepHeight)
        else:
            angle0=Leg_IK(0,-i*dYM,StepHeight)
        angle=angle0+angle0
        for j in range(len(names)):
            angleLists[j][i]=angle[j]
    motionProxy.angleInterpolation(names, angleLists, timeLists, True)
    t=0.2
    if right:
        angle0=Leg_IK(0,YM,StepHeight+UPHeight)
        motionProxy.angleInterpolation(names[5:10], angle0, [t,t,t,t,t], True)
        angle0=Leg_IK(Length,YM,StepHeight+UPHeight)
        motionProxy.angleInterpolation(names[5:10], angle0, [ts,ts,ts,ts,ts], True)
        time.sleep(0.1)
        angle0=Leg_IK(0,YM,StepHeight+UPHeight)
        motionProxy.angleInterpolation(names[5:10], angle0, [ts,ts,ts,ts,ts], True)
        angle0=Leg_IK(0,YM,StepHeight)
        motionProxy.angleInterpolation(names[5:10], angle0, [t,t,t,t,t], True)
        
    else:
        angle0=Leg_IK(0,-YM,StepHeight+UPHeight)
        motionProxy.angleInterpolation(names[0:5], angle0, [t,t,t,t,t], True)
        angle0=Leg_IK(Length,-YM,StepHeight+UPHeight)
        motionProxy.angleInterpolation(names[0:5], angle0, [ts,ts,ts,ts,ts], True)
        time.sleep(0.1)
        angle0=Leg_IK(0,-YM,StepHeight+UPHeight)
        motionProxy.angleInterpolation(names[0:5], angle0, [ts,ts,ts,ts,ts], True)
        angle0=Leg_IK(0,-YM,StepHeight)
        motionProxy.angleInterpolation(names[0:5], angle0, [t,t,t,t,t], True)
    # Move BC left or right
    for i in range(NM):
        if (right>0):
            angle0=Leg_IK(0,YM-i*dYM,StepHeight)
        else:
            angle0=Leg_IK(0,-YM+i*dYM,StepHeight)
        angle=angle0+angle0
        for j in range(len(names)):
            angleLists[j][i]=angle[j]
    motionProxy.angleInterpolation(names, angleLists, timeLists, True)'''
    Step_Start(motionProxy,right);
    Move_Leg(motionProxy,right,XS,0)
    for i in range(NM):
        if (right>0):
            angle0=Leg_IK(0,YM-i*dYM,StepHeight)
        else:
            angle0=Leg_IK(0,-YM+i*dYM,StepHeight)
        angle=angle0+angle0
        for j in range(len(names)):
            angleLists[j][i]=angle[j]
    motionProxy.angleInterpolation(names, angleLists, timeLists, True)
    
def main():
    #robotIP = "127.0.0.1"
    robotIP = "192.168.0.107"
    PORT = 9559
    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e
        sys.exit(1)

    # Send NAO to Pose Init
    #postureProxy.goToPosture("StandInit", StandInitSpeed)
    
    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
        # speechProxy = ALProxy("ALTextToSpeech", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)
    motionProxy.setStiffnesses(names, 1.0)
    Step_One(motionProxy,postureProxy,3)
    #TI(motionProxy,postureProxy,1,60,0.7)
    

if __name__ == "__main__":
    main()
    