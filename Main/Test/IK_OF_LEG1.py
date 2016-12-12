# -*- encoding: UTF-8 -*-

import sys
import time
from naoqi import ALProxy
from math import pi,sin,cos,asin,acos,atan2,sqrt

# Define Object
ThighLength=100.0
TibiaLength=102.90
X=170.0
R=80.0
L=60.0
N=100
Deta=pi/2.0/N
dL=2.0*L/N
dt=1.5/N


def IK(x,y,z):
    angle=[0,0,0,0,0]
    D2=x*x+y*y+z*z
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

def goPosition(robotIP,PORT,angles):
    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e
    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
        speechProxy = ALProxy("ALTextToSpeech", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)
        
    # joint
    names  = ["RHipRoll","RHipPitch","RKneePitch","RAnklePitch","RAnkleRoll"]
    motionProxy.setStiffnesses(names, 1.0)
    isAbsolute  = True
    # angles=IK(0,0,-ThighLength-TibiaLength+10)
    motionProxy.setAngles(names,angles,1);
    time.sleep(2);

def Draw(robotIP,PORT):
    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e

    # Send NAO to Pose Init
    postureProxy.goToPosture("StandZero", 0.5)
    
    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
        speechProxy = ALProxy("ALTextToSpeech", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)
        
    # joint
    names  = ["LShoulderPitch","LShoulderRoll","LElbowYaw","LElbowRoll","RShoulderPitch","RShoulderRoll","RElbowYaw","RElbowRoll"]
    motionProxy.setStiffnesses(names, 1.0)
    isAbsolute  = True
    
    #angleLists
    angleLists=[range(4*N) for i in range(len(names))]
    for i in range(4*N):
        ang=IK(X,R*cos(i*Deta),R*sin(i*Deta))
        angleLists[0][i]=ang[0]
        angleLists[1][i]=ang[1]
        angleLists[2][i]=ang[2]
        angleLists[3][i]=ang[3]
        if i<N :
            ang=IK(X,L,L-i*dL)   
        elif i<2*N :
            ang=IK(X,L-(i-N)*dL,-L)
        elif i<3*N :
            ang=IK(X,-L,(i-2*N)*dL-L)
        else :
            ang=IK(X,-L+(i-3*N)*dL,L)
        angleLists[4][i]=-ang[0]
        angleLists[5][i]=-ang[1]
        angleLists[6][i]=-ang[2]
        angleLists[7][i]=-ang[3]
        
    #timeLists
    timeLists=[[dt*(i+1) for i in range(4*N)] for i in range(len(names))]
    
    #print timeLists
    #print angleLists
    print "Start!"
    speechProxy.say("Notice! I'm moving!")
    
    initangles=[angleLists[0][0],angleLists[1][0],angleLists[2][0],angleLists[3][0],angleLists[4][0],angleLists[5][0],angleLists[6][0],angleLists[7][0]]
    
    motionProxy.setAngles(names, initangles, 0.2)
    
    time.sleep(1);
    
    motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)
    
    print "Done!"
    speechProxy.say("Done!")
    
    #postureProxy.goToPosture("Crouch", 0.5)
    
    motionProxy.setStiffnesses("Body", 0.0)

def main():
    robotIp = "127.0.0.1"
    #robotIp = "192.168.0.103"
    PORT = 9559
    
    if len(sys.argv) <= 1:
        print "Usage python Draw.py robotIP (optional default: 127.0.0.1)"
    else:
        robotIp = sys.argv[1]
        
    
    Draw(robotIp,PORT)
    
if __name__ == "__main__":
    #main()
    angle=IK(50,0,-ThighLength-TibiaLength+50)
    print(angle)
    robotIP = "127.0.0.1"
    PORT = 9559
    goPosition(robotIP,PORT,angle)
