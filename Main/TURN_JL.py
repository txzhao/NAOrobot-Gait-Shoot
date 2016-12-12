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
dh=30

def IK(x,y,z):
    angle=[0,0,0,0,0]
    z=z+-ThighLength-TibiaLength+dh
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
 
 # 1:turn left
def turn_clk(motionProxy,dre):
    if dre==0:
        return
    dre=-dre
    dre=dre*180.0/pi
    up=20
    names  = ["RHipRoll","RHipPitch","RKneePitch","RAnklePitch","RAnkleRoll","LHipRoll","LHipPitch","LKneePitch","LAnklePitch","LAnkleRoll","LHipYawPitch"]
    motionProxy.setStiffnesses(names, 1.0)
    num=6
    th=60
    speed=1

    if dre>0:
        flag=-1
    else:
        flag=1
        dre=-1*dre
    k=int(dre/23)
    if k!=1.0*dre/23:
        k=k+1
    aa=0.01234*-1*dre/k
    #print(k,aa,flag)

    
    angleLists=[range(num) for i in range(len(names))]
    angleLists2=[range(1) for i in range(len(names))]

    ang=IK(0,flag*th,0)
    ang2=IK(0,flag*th,0)
    i=0
    for j in range(5):
        angleLists[j][i]=ang[j]
    for j in range(5,10):
        angleLists[j][i]=ang2[j-5]
    angleLists[10][i]=0


    if flag==-1:
        ang=IK(0,-th,up)
        ang2=IK(0,-th,0)
    else:
        ang=IK(0,th,0)
        ang2=IK(0,th,up)
    i=1
    for j in range(5):
        angleLists[j][i]=ang[j]
    for j in range(5,10):
        angleLists[j][i]=ang2[j-5]
    angleLists[10][i]=-0

    if flag==-1:
        ang=IK(0,-th,up)
        ang2=IK(0,-th,0)
    else:
        ang=IK(0,th,0)
        ang2=IK(0,th,up)
    i=2
    for j in range(5):
        angleLists[j][i]=ang[j]
    for j in range(5,10):
        angleLists[j][i]=ang2[j-5]
    angleLists[10][i]=aa


    ang=IK(0,0,0)
    ang2=IK(0,0,0)
    i=3
    for j in range(5):
        angleLists[j][i]=ang[j]
    for j in range(5,10):
        angleLists[j][i]=ang2[j-5]
    angleLists[10][i]=aa

    if flag==1:
        ang=IK(0,-th,up)
        ang2=IK(0,-th,0)
    else:
        ang=IK(0,th,0)
        ang2=IK(0,th,up)
    i=4
    for j in range(5):
        angleLists[j][i]=ang[j]
    for j in range(5,10):
        angleLists[j][i]=ang2[j-5]
    angleLists[10][i]=aa

    ang=IK(0,-flag*th,0)
    ang2=IK(0,-flag*th,0)
    i=5
    for j in range(5):
        angleLists[j][i]=ang[j]
    for j in range(5,10):
        angleLists[j][i]=ang2[j-5]
    angleLists[10][i]=-0

    timeLists=[[speed*(i+1) for i in range(num)] for j in range(len(names))]
    #print('\n')
    #print(timeLists)
    
    #print(angleLists)

    for i in range(k):
        motionProxy.angleInterpolation(names, angleLists, timeLists, True)
    ang=IK(0,0,0)
    ang2=IK(0,0,0)
    i=0
    for j in range(5):
        angleLists2[j][i]=ang[j]
    for j in range(5,10):
        angleLists2[j][i]=ang2[j-5]
    timeLists=speed
    motionProxy.angleInterpolation(names, angleLists2, timeLists, True)
    
   
if __name__ == "__main__":
    #main()
    robotIP = "127.0.0.1"
    robotIP = "192.168.0.107"
    PORT = 9559
    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e

    # Send NAO to Pose Init
    postureProxy.goToPosture("StandInit", 3)
    
    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)
 
    turn_clk(motionProxy,pi/3)
    

