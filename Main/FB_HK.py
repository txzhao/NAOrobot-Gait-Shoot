import cv2 
import sys
import time  
import Image
import math
import numpy as np
from naoqi import ALProxy

DEBUG=1
Index0=0
Index1=0

# 0 up while 1 down
def showNaoImage(camProxy,camID):
    """
    First get an image from Nao, then show it on the screen with PIL.
    """
    camProxy.setParam(18,camID)

    resolution = 2    # VGA
    colorSpace = 11   # RGB
    
    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)
    
    
    # Get a camera image.    
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)
        
    # Time the image transfer.
        
    camProxy.unsubscribe(videoClient)
    
    
    # Now we work with the image returned and save it as a PNG  using ImageDraw
    # package.
    
    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]
    # Create a PIL Image from our pixel array.
    im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
    # Save the image.
    if camID==0:
        imName="C0_"+str(Index0)+".jpg"
    else:
        imName="C1_"+str(Index1)+".jpg"
    im.save(imName, "JPEG")
    return imName

def FB_DNC_Nor(img):
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #
    img[:,:,0] = cv2.equalizeHist(img[:,:,0]) 
    img[:,:,1] = cv2.equalizeHist(img[:,:,1]) 
    img[:,:,2] = cv2.equalizeHist(img[:,:,2])  
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  # 
    
    #
    bir = r>=200
    big = g<=65
    bib = b<60
    temp = np.logical_and(bir,big)
    binary = np.logical_and(temp,bib)
    bir = r>60
    big = g<=10
    bib = b<=10
    temp = np.logical_and(bir,big)
    temp = np.logical_and(temp,bib)
    binary = np.logical_or(temp,binary)
    
    # begin to find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    binary = np.array(binary,dtype=np.uint8)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    #findcontours
    contours, hierarchy = cv2.findContours(binary2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    if(len(contours)<1):
        return [0,0]
    area = 0
    k = 0
    for i in range(0,len(contours)):
        temp= cv2.contourArea(contours[i])
        if temp > area:
            k = i
            area = temp
    r0 = cv2.boundingRect(contours[k])
    distance = 2.123 * math.exp(-0.004135*(r0[1]+r0[3]))
    widthrate = 1.682*(r0[1]+r0[3])+139.7
    leveldistance = (r0[0] + r0[2]/2 - 333) / widthrate
    if DEBUG:
        cv2.drawContours(img,contours,k,(0,0,255),0)
        cv2.imshow("Ball_DN",img)
        cv2.imshow("binary2",binary2)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()
    return [distance,-leveldistance]

def FB_UPC_Nor(img):
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #
    img[:,:,0] = cv2.equalizeHist(img[:,:,0]) 
    img[:,:,1] = cv2.equalizeHist(img[:,:,1]) 
    img[:,:,2] = cv2.equalizeHist(img[:,:,2])  
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  #   
    
    #
    bir = r>=190
    big = np.logical_and(g<=180,g>90)
    bib = b<120
    temp = np.logical_and(bir,big)
    binary = np.logical_and(temp,bib)
    
    
    # begin to find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    binary = np.array(binary,dtype=np.uint8)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    #findcontours
    contours, hierarchy = cv2.findContours(binary2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    if len(contours)==0:
        return [0,0]
    area = 0
    k = 0
    for i in range(0,len(contours)):
        temp= cv2.contourArea(contours[i])
        if temp > area:
            k = i
            area = temp
    r0 = cv2.boundingRect(contours[k])
    distance = 461.6/((r0[1]+r0[3])-183.6)
    widthrate = 1.196*(r0[1]+r0[3])-221.4
    leveldistance = (r0[0] + r0[2]/2 - 340) / widthrate
    if DEBUG:   
        cv2.drawContours(img,contours,k,(0,0,255),0)
        cv2.imshow("Ball_UP",img)
        cv2.imshow("binary2",binary2)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()  
    return [distance,-leveldistance]

def FB_UPC_StandInit(img):
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  #   
    
    #
    bir = np.logical_and(r>=200,r<=260)
    big = np.logical_and(g>=9,g<=210)
    bib = np.logical_and(b>=30,b<=110)
    temp = np.logical_and(bir,big)
    binary = np.logical_and(temp,bib)
    
    # begin to find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    binary = np.array(binary,dtype=np.uint8)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    #findcontours
    contours, hierarchy = cv2.findContours(binary2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    
    area = 0
    k = 0
    if len(contours)>0:
        for i in range(0,len(contours)):
            temp= cv2.contourArea(contours[i])
            if temp > area:
                k = i
                area = temp
        r0 = cv2.boundingRect(contours[k])
        distance = 461.6/((r0[1]+r0[3])-183.6)
        widthrate = 1.196*(r0[1]+r0[3])-221.4
        leveldistance = (r0[0] + r0[2]/2 - 340) / widthrate
        if DEBUG:
            '''print 'distance:'
            print distance
            print 'leveldistance:'
            print -leveldistance'''
            cv2.drawContours(img,contours,k,(0,0,255),0)
            cv2.imshow("Ball_UP",img)
            cv2.imshow("binary2",binary2)
            cv2.waitKey(0)  
            cv2.destroyAllWindows()  
        return [distance,-leveldistance]
    else:
        if DEBUG:
            print "Try again\n" 
        return [0,0]

def FB_DNC_StandInit(img):
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  #   
    
    #
    bir = np.logical_and(r>=110,r<=240)
    big = np.logical_and(g>=10,g<=150)
    bib = np.logical_and(b>=10,b<=70)
    temp = np.logical_and(bir,big)
    binary = np.logical_and(temp,bib)
    
    # begin to find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    binary = np.array(binary,dtype=np.uint8)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    #findcontours
    contours, hierarchy = cv2.findContours(binary2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    
    area = 0
    k = 0
    if len(contours)>0:
        for i in range(0,len(contours)):
            temp= cv2.contourArea(contours[i])
            if temp > area:
                k = i
                area = temp
        r0 = cv2.boundingRect(contours[k])
        distance = 2.123 * math.exp(-0.004135*(r0[1]+r0[3]))
        widthrate = 1.682*(r0[1]+r0[3])+139.7
        leveldistance = (r0[0] + r0[2]/2 - 333) / widthrate
        if DEBUG:
            '''print 'distance:'
            print distance
            print 'leveldistance:'
            print -leveldistance'''
        
            cv2.drawContours(img,contours,k,(0,0,255),0)
            cv2.imshow("Ball_DN",img)
            cv2.imshow("binary2",binary2)
            cv2.waitKey(0)  
            cv2.destroyAllWindows()
        return [distance,-leveldistance]
    else:
        if DEBUG:
            print "Try again\n"
        return [0,0]

def FindBall(camProxy,camID):
    FileName=showNaoImage(camProxy,camID)
    img = cv2.imread(FileName)
    if camID==0:
        return FB_UPC_Nor(img)
    else:
        return FB_DNC_Nor(img)

#1:down
def FindBallAG(camProxy,camID):
    FileName=showNaoImage(camProxy,camID)
    img = cv2.imread(FileName)
    if camID==0:
        BallPos=FB_UPC_Nor(img)
        tmp=FBGate_UP_Nor(img)
        return [BallPos,tmp[0],tmp[1]]
    else:
        BallPos=FB_DNC_Nor(img)
        tmp=FBGate_DN_Nor(img)
        return [BallPos,tmp[0],tmp[1]]

def FBGate_UP_Nor(img):
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #
    img[:,:,0] = cv2.equalizeHist(img[:,:,0]) 
    img[:,:,1] = cv2.equalizeHist(img[:,:,1]) 
    img[:,:,2] = cv2.equalizeHist(img[:,:,2]) 
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  #   
    
    #
    bir = np.logical_and(r>=85,r<=160)
    big = np.logical_and(g>=130,g<=230)
    bib = np.logical_and(b>=190,b<=270)
    temp = np.logical_and(bir,big)
    binary = np.logical_and(temp,bib)
    
    # begin to find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    binary = np.array(binary,dtype=np.uint8)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    #findcontours
    contours, hierarchy = cv2.findContours(binary2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    if len(contours)<2:
        print 'Please Find Again!'
        return [[0,0],[0,0]]
    # area1 tells the largest; area2 tells the second largest; they are temporary.
    area1 = 0
    area2 = 0
    k1 = 0
    k2 = 0
    for i in range(0,len(contours)):
        temp= cv2.contourArea(contours[i])
        if temp > area1:
            k2 = k1
            k1 = i
            area2 = area1
            area1 = temp
        elif temp > area2:
            k2 = i
            area2 = temp
        else:
            temp = temp
    r1 = cv2.boundingRect(contours[k1])
    r2 = cv2.boundingRect(contours[k2])
    if cv2.contourArea(contours[k2])<50:
        return [[0,0],[0,0]]
    #1
    distance1 = 461.6/((r1[1]+r1[3])-183.6)
    widthrate1 = 1.196*(r1[1]+r1[3])-221.4
    leveldistance1 = (r1[0] + r1[2]/2 - 340) / widthrate1
    #2
    distance2 = 461.6/((r2[1]+r2[3])-183.6)
    widthrate2 = 1.196*(r2[1]+r2[3])-221.4
    leveldistance2 = (r2[0] + r2[2]/2 - 340) / widthrate2
    if DEBUG:
        '''print 'distance1:'
        print distance1
        print 'leveldistance1:'
        print -leveldistance1
        print 'distance2:'
        print distance2
        print 'leveldistance2:'
        print -leveldistance2'''
        
        cv2.drawContours(img,contours,k1,(0,0,255),0)
        cv2.drawContours(img,contours,k2,(0,0,255),0)
        cv2.imshow("Gate_UP",img)
        cv2.imshow("binary2",binary2)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()  
    return [[distance1,-leveldistance1],[distance2,-leveldistance2]]

def FBGate_DN_Nor(img):
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #  
    img[:,:,0] = cv2.equalizeHist(img[:,:,0]) 
    img[:,:,1] = cv2.equalizeHist(img[:,:,1]) 
    img[:,:,2] = cv2.equalizeHist(img[:,:,2])  
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  #
    
    #
    bir = r<=60
    big = g<=120
    bib = b>205
    temp = np.logical_and(bir,big)
    binary = np.logical_and(temp,bib)
    bir = r<=20
    big = g<=20
    bib = b>100
    temp = np.logical_and(bir,big)
    temp = np.logical_and(temp,bib)
    binary = np.logical_or(temp,binary)
    
    # begin to find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    binary = np.array(binary,dtype=np.uint8)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    #findcontours
    contours, hierarchy = cv2.findContours(binary2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    
    if len(contours)<2 :
        print 'Please Find Again!'
        return [[0,0],[0,0]]
    
    # area1 tells the largest; area2 tells the second largest; they are temporary.
    area1 = 0
    area2 = 0
    k1 = 0
    k2 = 0
    for i in range(0,len(contours)):
        temp= cv2.contourArea(contours[i])
        if temp > area1:
            k2 = k1
            k1 = i
            area2 = area1
            area1 = temp
        elif temp > area2:
            k2 = i
            area2 = temp
        else:
            temp = temp
    r1 = cv2.boundingRect(contours[k1])
    r2 = cv2.boundingRect(contours[k2])
    
    if cv2.contourArea(contours[k2])<50:
        return [[0,0],[0,0]]
    #largest
    distance1 = 2.123 * math.exp(-0.004135*(r1[1]+r1[3]))
    widthrate1 = 1.682*(r1[1]+r1[3])+139.7
    leveldistance1 = (r1[0] + r1[2]/2 - 333) / widthrate1
    #secondlargest
    distance2 = 2.123 * math.exp(-0.004135*(r2[1]+r2[3]))
    widthrate2 = 1.682*(r2[1]+r2[3])+139.7
    leveldistance2 = (r2[0] + r2[2]/2 - 333) / widthrate2
    if DEBUG:
    #1
        '''print 'distance1:'
        print distance1
        print 'leveldistance1:'
        print -leveldistance1
        #2
        print 'distance2:'
        print distance2
        print 'leveldistance2:'
        print -leveldistance2'''
        
        cv2.drawContours(img,contours,k1,(0,0,255),0)
        cv2.drawContours(img,contours,k2,(0,0,255),0)
        cv2.imshow("Gate_DN",img)
        cv2.imshow("binary2",binary2)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()  
    return [[distance1,-leveldistance1],[distance2,-leveldistance2]]

def FBGate_UP(img):
    #code Here
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  #   
    
    #
    bir = np.logical_and(r>=69,r<=127)
    big = np.logical_and(g>=170,g<=220)
    bib = np.logical_and(b>=210,b<=260)
    temp = np.logical_and(bir,big)
    binary = np.logical_and(temp,bib)
    
    # begin to find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    binary = np.array(binary,dtype=np.uint8)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    #findcontours
    contours, hierarchy = cv2.findContours(binary2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    if len(contours)<2:
        return [[0,0],[0,0]]
    # area1 tells the largest; area2 tells the second largest; they are temporary.
    area1 = 0
    area2 = 0
    k1 = 0
    k2 = 0
    for i in range(0,len(contours)):
        temp= cv2.contourArea(contours[i])
        if temp > area1:
            k2 = k1
            k1 = i
            area2 = area1
            area1 = temp
        elif temp > area2:
            k2 = i
            area2 = temp
        else:
            temp = temp
    r1 = cv2.boundingRect(contours[k1])
    r2 = cv2.boundingRect(contours[k2])
    if cv2.contourArea(contours[k2])<50:
        return [[0,0],[0,0]]
    #1
    distance1 = 461.6/((r1[1]+r1[3])-183.6)
    widthrate1 = 1.196*(r1[1]+r1[3])-221.4
    leveldistance1 = (r1[0] + r1[2]/2 - 340) / widthrate1
    #2
    distance2 = 461.6/((r2[1]+r2[3])-183.6)
    widthrate2 = 1.196*(r2[1]+r2[3])-221.4
    leveldistance2 = (r2[0] + r2[2]/2 - 340) / widthrate2
    if DEBUG:
        print 'distance1:'
        print distance1
        print 'leveldistance1:'
        print -leveldistance1
        print 'distance2:'
        print distance2
        print 'leveldistance2:'
        print -leveldistance2
        
        cv2.drawContours(img,contours,k1,(0,0,255),0)
        cv2.drawContours(img,contours,k2,(0,0,255),0)
        cv2.imshow("Gate_UP",img)
        cv2.imshow("binary2",binary2)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()  
    return [[distance1,-leveldistance1],[distance2,-leveldistance2]]
    
def FBGate_DN(img):
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  #   
    
    #
    bir = np.logical_and(r>=5,r<=60)
    big = np.logical_and(g>=40,g<=125)
    bib = np.logical_and(b>=80,b<=195)
    temp = np.logical_and(bir,big)
    binary = np.logical_and(temp,bib)
    
    # begin to find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5, 5))
    binary = np.array(binary,dtype=np.uint8)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    binary2 = cv2.dilate(binary,kernel)
    #findcontours
    contours, hierarchy = cv2.findContours(binary2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    
    if len(contours)<2 :
        print 'Please Find Again!'
        return [[0,0],[0,0]]
    # area1 tells the largest; area2 tells the second largest; they are temporary.
    area1 = 0
    area2 = 0
    k1 = 0
    k2 = 0
    for i in range(0,len(contours)):
        temp= cv2.contourArea(contours[i])
        if temp > area1:
            k2 = k1
            k1 = i
            area2 = area1
            area1 = temp
        elif temp > area2:
            k2 = i
            area2 = temp
        else:
            temp = temp
    r1 = cv2.boundingRect(contours[k1])
    r2 = cv2.boundingRect(contours[k2])
    if cv2.contourArea(contours[k2])<50:
        return [[0,0],[0,0]]
    #largest
    distance1 = 2.123 * math.exp(-0.004135*(r1[1]+r1[3]))
    widthrate1 = 1.682*(r1[1]+r1[3])+139.7
    leveldistance1 = (r1[0] + r1[2]/2 - 333) / widthrate1
    #secondlargest
    distance2 = 2.123 * math.exp(-0.004135*(r2[1]+r2[3]))
    widthrate2 = 1.682*(r2[1]+r2[3])+139.7
    leveldistance2 = (r2[0] + r2[2]/2 - 333) / widthrate2
    if DEBUG:
        #1
        print 'distance1:'
        print distance1
        print 'leveldistance1:'
        print -leveldistance1
        #2
        print 'distance2:'
        print distance2
        print 'leveldistance2:'
        print -leveldistance2
        
        cv2.drawContours(img,contours,k1,(0,0,255),0)
        cv2.drawContours(img,contours,k2,(0,0,255),0)
        cv2.imshow("Gate_DN",img)
        cv2.imshow("binary2",binary2)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()  
    return [[distance1,-leveldistance1],[distance2,-leveldistance2]]



    
def main():
    IP = "192.168.0.107"  # Replace here with your NaoQi's IP address.
    PORT = 9559
    try:
        camProxy = ALProxy("ALVideoDevice", IP, PORT)
    except Exception, e:
        print "Could not create proxy to ALVideoDevice"
        print "Error was: ", e
        sys.exit(1)
    FindBall(camProxy,0)

if __name__ == "__main__":
    main()