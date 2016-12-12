from STEP_ZY_CP import Step_One,TI,XS_Init,Step_Init,Step_Go
from TURN_JL import turn_clk
from FB_HK import FindBall,FindBallAG
import sys
import time
from naoqi import ALProxy
from math import pi,atan,atan2

# TurnHeadAngle=pi/4
TurnTolAngle=pi/16
FloorLen=520.0
MinTurnPoint=300.0
TurnSeeAngleList=[0,pi/4,-pi/2,-pi/4,-pi]

def GetBallPos(motionProxy,camProxy):
    camID=1
    BallPos=[0,0]
    flag=1
    while flag:
        for TurnSeeAngle in TurnSeeAngleList:
            turn_clk(motionProxy,TurnSeeAngle)
            for camID in [1,0]:
                BallPos=FindBall(camProxy,camID)
                if BallPos[0]>0:
                    flag=0
                    break
            if flag==0:
                break
        if flag:
            turn_clk(motionProxy,4)
    BallPos[0]=BallPos[0]*FloorLen
    BallPos[1]=BallPos[1]*FloorLen
    return BallPos

def TiBall(motionProxy,camProxy):
    BallPos=GetBallPos(motionProxy,camProxy)
    turnAngles=atan(BallPos[1]/BallPos[0])
    if abs(turnAngles)>=pi/12:
        turn_clk(motionProxy,turnAngles)
        BallPos=GetBallPos(motionProxy,camProxy)
    if BallPos[0]>MinTurnPoint:
        stepTimes=int((BallPos[0]-MinTurnPoint)/XS_Init)
        Step_One(motionProxy,stepTimes)
        BallPos=GetBallPos(motionProxy,camProxy)
        turnAngles=atan(BallPos[1]/BallPos[0])
        if abs(turnAngles)>=pi/12:
            turn_clk(motionProxy,turnAngles)
            BallPos=GetBallPos(motionProxy,camProxy)  
    stepTimes=int((BallPos[0])/XS_Init)
    Step_One(motionProxy,stepTimes)
    if(BallPos[1]>0):
        TI(motionProxy,1)
    else:
        TI(motionProxy,0)


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
    postureProxy.goToPosture("StandInit", 0.5)
    
    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
        # speechProxy = ALProxy("ALTextToSpeech", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)
        
    try:
        camProxy = ALProxy("ALVideoDevice", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALVideoDevice"
        print "Error was: ", e
        sys.exit(1)
    Step_Init(motionProxy)
    TiBall(motionProxy,camProxy)
    '''while 1:
        raw_input()
        print FindBallAG(camProxy,1)
        print FindBallAG(camProxy,0)'''
    
    #Step_Go(motionProxy,FloorLen)
    #print FindBall(camProxy,1)
    #print FindBall(camProxy,0)
    
    
if __name__ == "__main__":
    main()