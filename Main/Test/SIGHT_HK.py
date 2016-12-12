import cv2 
import sys
import time  
import Image
import numpy as np
from naoqi import ALProxy

DEBUG=1

def showNaoImage(camProxy):
    """
    First get an image from Nao, then show it on the screen with PIL.
    """
    
    resolution = 2    # VGA
    colorSpace = 11   # RGB
    
    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)
    t0 = time.time()
    
    # Get a camera image.    
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)
    
    t1 = time.time()
    
    # Time the image transfer.
    print "acquisition delay ", t1 - t0
    
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
    imName="camImage.jpg"
    im.save(imName, "JPEG")
    return imName

def saveNaoImage(camProxy):
    """
    First get an image from Nao, then show it on the screen with PIL.
    """
    
    resolution = 2    # VGA
    colorSpace = 11   # RGB
    
    camProxy.setParam(18,1)
    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)
    t0 = time.time()
    
    # Get a camera image.    
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)
    
    t1 = time.time()
    
    # Time the image transfer.
    print "acquisition delay ", t1 - t0
    
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
    imName="C1_"+str(t1)+".jpg"
    im.save(imName, "JPEG")
    
    camProxy.setParam(18,0)
    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)
    
    # Get a camera image.    
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)
        
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
    imName="C0_"+str(t1)+".jpg"
    im.save(imName, "JPEG")
    return imName

def Sight(img): 
    #b, g, r = cv2.split(img)
    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # use thred judgement to every channel
    #bir = np.logical_and(r>=130,r<=240)
    #binary = np.logical_and(b,g,r)
    #retb, bib = cv2.threshold(b,15,70,cv2.THRESH_BINARY)
    #contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(img,contours,-1,(0,0,255),3)
    #
    b = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    g = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
    r = np.zeros((img.shape[0],img.shape[1]),dtype=img.dtype)  
      
    #
    b[:,:] = img[:,:,0]  #   
    g[:,:] = img[:,:,1]  #   
    r[:,:] = img[:,:,2]  #   
    
    #
    bir = np.logical_and(r>=130,r<=240)
    big = np.logical_and(g>=40,g<=150)
    bib = np.logical_and(b>=15,b<=70)
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
    if(len(contours)>0):
        for i in range(0,len(contours)):
            temp= cv2.contourArea(contours[i])
            if temp > area:
                k = i
                area = temp
        r0 = cv2.boundingRect(contours[i])
        distance = 65.06 * pow(  (r0[1]+r0[3])  ,  (-0.5388)  )-1.791
        widthrate = 461.1 * pow( distance , -0.8764)
        leveldistance = (r0[0] + r0[2]/2 - 320) / widthrate
        '''print 'distance:'
        print distance
        print 'leveldistance:'
        print leveldistance'''
        
        if DEBUG:
            cv2.drawContours(img,contours,k,(0,0,255),0)
            cv2.imshow("Img",img)
            cv2.imshow("binary2",binary2)
            cv2.waitKey(0)  
            cv2.destroyAllWindows() 
        return [distance,-leveldistance]
    else:
        return [0,0]

def SearchBall(camProxy):
    imName=showNaoImage(camProxy)
    img = cv2.imread(imName)
    return Sight(img)


def main():
    IP = "192.168.0.107"  # Replace here with your NaoQi's IP address.
    PORT = 9559
    try:
        camProxy = ALProxy("ALVideoDevice", IP, PORT)
    except Exception, e:
        print "Could not create proxy to ALVideoDevice"
        print "Error was: ", e
        sys.exit(1)
    camProxy.setParam(18,1)
    print SearchBall(camProxy)
    

if __name__ == "__main__":
    #img = cv2.imread("F:\\Image\\Anime\\AB.jpg")
    
    #print Sight(img) 
    main()