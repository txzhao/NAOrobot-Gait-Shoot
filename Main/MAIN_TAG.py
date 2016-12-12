from STEP_ZY_CP import Step_One,TI,XS_Init,Step_Init,Step_Go
from TURN_JL import turn_clk
from FB_HK import FindBall,FindBallAG
import sys
import time
from naoqi import ALProxy
from math import pi,atan,cos,sin,sqrt,acos,atan2

# TurnHeadAngle=pi/4
TurnTolAngle=pi/16
FloorLen=520.0
MinTurnPoint=300.0
LenReady=360.0
TurnSeeAngleList=[0,pi/6,pi/6,pi/6,pi/6,pi/6,pi/6,pi/6,pi/6,pi/6,pi/6,pi/6,pi/6]

'''#times>0 turn left
def TurnHead(motionProxy,times):
    name="HeadYaw"
    MaxSpeed  = 0.2
    angle=times*TurnHeadAngle
    motionProxy.setAngles(name, angle, MaxSpeed)
    time.sleep(3.0)'''

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

def GetBAGPos(motionProxy,camProxy):
    camID=1
    BallPos=[0,0]
    GatePos=[0,0]
    flag=1
    while flag:
        for TurnSeeAngle in TurnSeeAngleList:
            turn_clk(motionProxy,TurnSeeAngle)
            camID=1
            TmpPos=FindBallAG(camProxy,camID)
            if TmpPos[0][0]>0:
                BallPos=TmpPos[0]
            if TmpPos[1][0]>0:
                GatePos[0]=(TmpPos[1][0]+TmpPos[2][0])/2
                GatePos[1]=(TmpPos[1][1]+TmpPos[2][1])/2
            if BallPos[0] and GatePos[0]:
                flag=0
                break
            camID=0
            TmpPos=FindBallAG(camProxy,camID)
            if TmpPos[0][0]>0:
                BallPos=TmpPos[0]
            if TmpPos[1][0]>0:
                GatePos[0]=(TmpPos[1][0]+TmpPos[2][0])/2
                GatePos[1]=(TmpPos[1][1]+TmpPos[2][1])/2
            if BallPos[0] and GatePos[0]:
                flag=0
                break
            # Switch position
            fcos=cos(TurnSeeAngle)
            fsin=sin(TurnSeeAngle)
            if BallPos[0]:
                tmp=BallPos[:]
                BallPos[0]=tmp[0]*fcos+tmp[1]*fsin
                BallPos[1]=-tmp[0]*fsin+tmp[1]*fcos
            if GatePos[0]:
                tmp=GatePos[:]
                GatePos[0]=tmp[0]*fcos+tmp[1]*fsin
                GatePos[1]=-tmp[0]*fsin+tmp[1]*fcos
        if flag:
            turn_clk(motionProxy,4)
            print "Try again"
    BallPos[0]=BallPos[0]*FloorLen
    BallPos[1]=BallPos[1]*FloorLen
    GatePos[0]=GatePos[0]*FloorLen
    GatePos[1]=GatePos[1]*FloorLen
    return [BallPos,GatePos]

def TiBall(motionProxy,camProxy):
    BallPos=GetBallPos(motionProxy,camProxy)
    turnAngles=atan(BallPos[1]/BallPos[0])
    if abs(turnAngles)>=pi/16:
        turn_clk(motionProxy,turnAngles)
        BallPos=GetBallPos(motionProxy,camProxy)
    if BallPos[0]>MinTurnPoint:
        stepTimes=int((BallPos[0]-MinTurnPoint)/XS_Init)
        Step_One(motionProxy,stepTimes)
        BallPos=GetBallPos(motionProxy,camProxy)
        turnAngles=atan(BallPos[1]/BallPos[0])
        if abs(turnAngles)>=pi/16:
            turn_clk(motionProxy,turnAngles)
            BallPos=GetBallPos(motionProxy,camProxy)  
    #stepTimes=int((BallPos[0])/XS_Init)
    #Step_One(motionProxy,stepTimes)
    Step_Go(motionProxy,BallPos[0]-30)
    if(BallPos[1]>0):
        TI(motionProxy,1)
    else:
        TI(motionProxy,0)

def DisOfTwo(P1,P2):
    a=P1[0]-P2[0]
    b=P1[1]-P2[1]
    return sqrt(a*a+b*b)

def TIBallTG(motionProxy,camProxy):
    for i in range(2):
        [BallPos,GatePos]=GetBAGPos(motionProxy,camProxy)
        #[BallPos,GatePos]=[[FloorLen,0],[FloorLen,-FloorLen]]
        
        LenBallGate=DisOfTwo(BallPos,GatePos)
        TerPos=[0,0]
        TerPos[0]=(BallPos[0]-GatePos[0])*LenReady/LenBallGate+BallPos[0]
        TerPos[1]=(BallPos[1]-GatePos[1])*LenReady/LenBallGate+BallPos[1]
        LenTer=DisOfTwo(TerPos,[0,0])
        AngleTer=atan2(TerPos[1],TerPos[0])
        turn_clk(motionProxy,AngleTer)
        print "Go "+str(LenTer)+"\n"
        Step_Go(motionProxy,LenTer)
        fcos=cos(AngleTer)
        fsin=sin(AngleTer)
        tmp=GatePos[:]
        GatePos[0]=tmp[0]*fcos+tmp[1]*fsin-LenTer
        GatePos[1]=-tmp[0]*fsin+tmp[1]*fcos
        turnAngle=atan2(GatePos[1],GatePos[0])
        #turnAngle=pi-acos((LenTer*LenTer+LenReady*LenReady-LenBall*LenBall)/(2*LenTer*LenReady))
        turn_clk(motionProxy,turnAngle)
        [BallPos,GatePos]=GetBAGPos(motionProxy,camProxy)
        AB=atan2(BallPos[1],BallPos[0])
        AG=atan2(GatePos[1],GatePos[0])
        print str(i)+"_th iteration\n" 
        if (abs(AG-AB)<pi/30):
            break
    print "Start Ti\n"
    #TiBall(motionProxy,camProxy)
    BallPos=GetBallPos(motionProxy,camProxy)
    turnAngles=atan(BallPos[1]/BallPos[0])
    if abs(turnAngles)>=pi/16:
        turn_clk(motionProxy,turnAngles)
        BallPos=GetBallPos(motionProxy,camProxy)
    if BallPos[0]>MinTurnPoint:
        stepTimes=int((BallPos[0]-MinTurnPoint)/XS_Init)
        Step_One(motionProxy,stepTimes)
        [BallPos,GatePos]=GetBAGPos(motionProxy,camProxy)
        turnAngles=atan(GatePos[1]/GatePos[0])
        if abs(turnAngles)>=pi/16:
            turn_clk(motionProxy,turnAngles)
            BallPos=GetBallPos(motionProxy,camProxy)  
    #stepTimes=int((BallPos[0])/XS_Init)
    #Step_One(motionProxy,stepTimes)
    Step_Go(motionProxy,BallPos[0]-30)
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
    #Step_Go(motionProxy,FloorLen)
    TIBallTG(motionProxy,camProxy)
    #TiBall(motionProxy,camProxy)
    #print FindBall(camProxy,1)
    #print FindBall(camProxy,0)
    
    
if __name__ == "__main__":
    main()