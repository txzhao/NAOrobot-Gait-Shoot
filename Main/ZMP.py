# -*- encoding: UTF-8 -*-

import sys
import time
from naoqi import ALProxy
from naoqi import ALBroker
from optparse import OptionParser

LKua=50.0

#SFR Key Names
LFsrNames=( "Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/Value",
            "Device/SubDeviceList/LFoot/FSR/FrontRight/Sensor/Value",
            "Device/SubDeviceList/LFoot/FSR/RearLeft/Sensor/Value",
            "Device/SubDeviceList/LFoot/FSR/RearRight/Sensor/Value")
            
RFsrNames=( "Device/SubDeviceList/RFoot/FSR/FrontLeft/Sensor/Value",
            "Device/SubDeviceList/RFoot/FSR/FrontRight/Sensor/Value",
            "Device/SubDeviceList/RFoot/FSR/RearLeft/Sensor/Value",
            "Device/SubDeviceList/RFoot/FSR/RearRight/Sensor/Value")

#FSR Position
LFsrPosX=(70.25,70.25,-30.25,-29.65)
LFsrPosY=(29.90,-23.10,29.90,-19.10)
RFsrPosX=(70.25,70.25,-30.25,-29.65)
RFsrPosY=(23.10,-29.90,19.10,-29.90)

#FSR Data
LFsrData=[0.0 for i in range(4)]
RFsrData=[0.0 for i in range(4)]

def getZMP(PR,PL):
    memory = ALProxy("ALMemory")
    LxSUMFsrData=0.0
    LySUMFsrData=0.0
    RxSUMFsrData=0.0
    RySUMFsrData=0.0
    for i in range(4):
        LFsrData[i]=memory.getData(LFsrNames[i])
        RFsrData[i]=memory.getData(RFsrNames[i])
        LxSUMFsrData=LxSUMFsrData+LFsrData[i]*LFsrPosX[i]
        LySUMFsrData=LySUMFsrData+LFsrData[i]*LFsrPosY[i]
        RxSUMFsrData=RxSUMFsrData+RFsrData[i]*RFsrPosX[i]
        RySUMFsrData=RySUMFsrData+RFsrData[i]*RFsrPosY[i]
    #sum FSR of Left and Right
    LSUMF=sum(LFsrData)
    RSUMF=sum(RFsrData)
    SUMF=LSUMF+RSUMF
    #ZMP of Left and Right
    LPx=LxSUMFsrData/LSUMF+PL[0]+LKua
    LPy=LySUMFsrData/LSUMF+PL[1]
    RPx=RxSUMFsrData/RSUMF+PR[0]-LKua
    RPy=RySUMFsrData/RSUMF+PL[1]
    #Double
    Px=(LPx*LSUMF+RPx*RSUMF)/SUMF
    Py=(LPy*LSUMF+RPy*RSUMF)/SUMF
    return [Px,Py]

if __name__ == "__main__":
    robotIp = "127.0.0.1"
    #robotIp = "192.168.0.107"
    PORT = 9559
    
    if len(sys.argv) <= 1:
        print "Usage python Draw.py robotIP (optional default: 127.0.0.1)"
    else:
        robotIp = sys.argv[1]
    
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=robotIp,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port
    while 1:
        ZMP=getZMP([0,0],[0,0])
        time.sleep(0.1)
        print ZMP
    myBroker.shutdown()
    sys.exit(0)
    
    