import cv2
import numpy as np
from mtcnn import MTCNN

camera = cv2.VideoCapture(0)
camera.set(3,640)
camera.set(4,480)
detector = MTCNN()


while(True):
    ret, img = camera.read()
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    results = detector.detect_faces(img)

    for face in results:
        x,y,w,h = face["box"]

        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

        
    cv2.imshow('img',img)

    k = cv2.waitKey(100) & 0xff
    if k ==27:
        break


camera.release()
cv2.destroyAllWindows() 