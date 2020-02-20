# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import struct
import socket
import math
npzFile = np.load('cam06.npz')
dist = npzFile['dist']
mtx = npzFile['mtx']
newcameramtx = npzFile['newcameramtx']
roi = npzFile['roi']

#defines udp server address for jetson
HOST = '10.8.88.19'
PORT = 5809

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind((HOST, PORT))

#message = None
#rioAddress = ('10.8.88.2', 5555)

otherAddress = None

camera = cv2.VideoCapture(0)

lowerRed = np.array([0,0, 160])
upperRed = np.array([130,100, 255])
lowerGreen = np.array([150,190,50])
upperGreen = np.array([255,255,160])
objP = np.array([(-19.625, 0,0), (-17.315, 0,0), (-9.8125, -17,0), (-8.8125, -15,0), (8.8125, -15,0), (9.8125, -17,0), (17.315, 0,0), (19.625, 0,0)], dtype = np.float32())
sortLen = len(objP)
failNum = 0
"""
Anything that is labeled #Visual should be commented out before a conversion to an executable
"""

# keep looping
print "looking"
while True:
        # grab the current frame
        (grabbed, frame) = camera.read()
        frame = cv2.undistort(frame, mtx, dist, None, newcameramtx)
        rvec = None
        tvec = None
        """
        while otherAddress is None:
                try:
           
                        cycle, otherAddress = sock.recvfrom(65507)
                        print cycle
                        print otherAddress

                except Exception:
                        cycle = None
                        rioAddress = None
        """
        frame = cv2.GaussianBlur(frame, (3,3), 0)
        frame2 = frame.copy()
        redMask = cv2.inRange(frame, lowerRed, upperRed)
        greenMask = cv2.inRange(frame, lowerGreen, upperGreen)
        #redEdges = cv2.Canny(redMask, 75, 150)
        #def onmouse(k, x, y, s, p):
                #global frame2
                #if k==1:
                        #print frame2[y,x]
        #cv2.namedWindow("frame2")
        #cv2.setMouseCallback("frame2",onmouse)
        contours, heirarchy = cv2.findContours(greenMask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        #contours2, heirarchy2 = cv2.findContours(redEdges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        if len(contours) > 0:
                cv2.drawContours(frame, contours, 0, (255, 0, 0), 1) #Visual
                c = max(contours, key=cv2.contourArea)
                epsilon = 0.01*cv2.arcLength(c,True)
                approx = cv2.approxPolyDP(c,epsilon,True)

                for a in approx: #Visual
                        cv2.circle(frame, (a[0][0], a[0][1]), 3, (255, 0, 255), -1) #Visual

                #print len(approx)

                if len(approx) == sortLen: #Only try to calculate distance if correct number of points are found
                        sortApprox = sorted(approx, key=lambda k: [k[:,0], k[:,1]])
                        sortApprox = np.array(sortApprox)

                        for i in range(len(sortApprox[:,0])):
                                if i % 2 == 0:
                                        approx1 = sortApprox[i][0].copy()
                                        approx2 = sortApprox[i+1][0].copy()
                                        if (approx1[1] < approx2[1]):
                                                sortApprox[i][0] = approx2.copy()
                                                sortApprox[i+1][0] = approx1.copy()

                        sortApprox = np.array(sortApprox)
                        sortApprox = sortApprox.astype(np.float32)
                        retval, rvec, tvec = cv2.solvePnP(objP, sortApprox, mtx, None)
                        angle = math.atan(tvec[0] / tvec[2])
                        angle = math.degrees(angle)
                        inches = tvec[2]
                        cv2.putText(frame, "%.2fft" % (inches/12), (frame.shape[1]-200, frame.shape[0]-20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2.0, (0, 255, 0), 3) #Visual
                        cv2.putText(frame, "%.2fft" % (tvec[0]/12), (frame.shape[1]-200, frame.shape[0]-70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2.0, (0, 255, 0), 3) #Visual
                        cv2.putText(frame, "%.2f" % angle, (frame.shape[1]-200, frame.shape[0]-120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2.0, (0, 255, 0), 3) #Visual
        """
        if otherAddress is not None:
                if rvec is not None and tvec is not None:
                        print "send good"
                        print tvec
                        print rvec
                        send = struct.pack("!ffffff", float(tvec[0][0]), float(tvec[1][0]), float(tvec[2][0]), float(rvec[0][0]), float(rvec[1][0]), float(rvec[2][0]))
                        sock.sendto(send, rioAddress)
                        failNum = 0

                else:
                        
                        failNum += 1
                        if failNum > 60: #If it can't find a target in x number of frames, send error numbers
                                #print "big oof"
                                send = struct.pack("!ffffff", -99.9, -99.9, -99.9, -99.9, -99.9, -99.9)
                                sock.sendto(send, rioAddress)
                        else:
                                print "small oof"
        """
        cv2.imshow("frame", frame) #Visual
        #cv2.imshow("frame2", frame2)
        cv2.imshow("greenMask", greenMask) #Visual
        #cv2.imshow("RedEdges", redEdges)
        #cv2.imshow("redMask", redMask) #Visual
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
                break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()