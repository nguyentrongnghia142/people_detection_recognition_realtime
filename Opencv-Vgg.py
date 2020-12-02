# import matplotlib.pyplot as plt 
from PIL import Image
from keras_vggface.vggface import VGGFace 
import cv2
from scipy.spatial.distance import cosine
from keras_vggface.utils import preprocess_input
import numpy as np 
import os
from imutils.video import FPS
import argparse
import time
import imutils
import math
import freenect
from serial import Serial

	

#The following line is for serial over GPIO
port = '/dev/ttyUSB'
for i in range(4):
    try:
        arduino = Serial(port+str(i),9600,timeout=5)
    except:
        print("error")

def face_identify(modelvgg,net, threshold_confidence,thresh = 0.4):
    # class model net 
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat","bottle", "bus", "car", "cat", "chair", "cow", "diningtable","dog", "horse", "motorbike", "person", "pottedplant", "sheep",	"sofa", "train", "admonitory"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    # source Face 
    cascadePath = "haarcascade_frontalface_default.xml"
    facecascade = cv2.CascadeClassifier(cascadePath)
    # font 
    font = cv2.FONT_HERSHEY_SIMPLEX
    print("[INFO] starting video stream...")
#     cam = cv2.VideoCapture(0) # /dev/video0 
#     cam.set(3,640)
#     cam.set(4,480)
    minW = 64
    minH = 48
    # get face database
#     fps = FPS().start()
    data_face ,persons = get_dataset()
    pred_dataset = get_embedding(data_face,model)


    tracking = False
    centroid_tracking = None
    mission = None
    counter = 0
    while True:
        track = {}
        
        # get frame 
        frame = get_video()
        t0 = time.time()
        frame = imutils.resize(frame,width = 640)
        # img = frame
        
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),0.007843, (300, 300), 127.5)

        net.setInput(blob)
        detections = net.forward()
        # detection face img
        for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
            confidence = detections[0, 0, i, 2]

            if confidence > threshold_confidence:
            
                idx = int(detections[0, 0, i, 1])
                if idx == 15:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # draw the prediction on the frame
                    label = "{}: {:.2f}%".format(CLASSES[idx],confidence * 100)
                    cv2.rectangle(frame, (startX, startY), (endX, endY),COLORS[idx], 2) 
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),font, 0.5, COLORS[idx], 2)
                    # detection Face in Person
                    img = frame[startY:endY,startX:endX] 

                    faces = facecascade.detectMultiScale( 
                        img,
                        scaleFactor = 1.2,
                        minNeighbors = 5,
                        minSize = (int(minW),int(minH)),
                    )
                    id = "unknown"
                    
                    # face recognition 
                    for (x,y,w,h) in faces:
                        face = img[y:y+h,x:x+w] # 1
                        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2) # 1
                        # face = preprocess_face(face)
                        pred = get_embedding([face],model)

                        for index ,emb in enumerate(pred_dataset[:]):
                            # print(len(pred[:-1]))
                            score = cosine(emb,pred[0])
                            if (score < thresh):
                                id = persons[index]
                                break
                            
                        cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)

                    centroid = (int((startX+endX)/2) ,int((startY+endY)/2)) 
                    if (id in persons and (mission ==None or mission == id)):
                        centroid_tracking= centroid
                        mission = id
                        print(centroid_tracking)
                    
                    
                    print(mission)
                    if mission != None:
                        track[centroid] = distance(centroid,centroid_tracking)
                        coordination(centroid_tracking, frame) 

        if tracking != None and track:          
            keymin = min(track,key = track.get) 
            cv2.circle(frame,(keymin[0],keymin[1]),radius = 10,color = (0,0,255))  
            centroid_tracking = keymin
          

        if not track:
            counter += 1
            if counter == 10:
                mission = None 
                counter = 0

        cv2.imshow('Detection and FaceRecognition',frame) 
        print("Execution time: %.4f(s)" % (time.time() - t0))

        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break

#         fps.update()
# 
#     fps.stop()
#     print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
#     print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

#     cam.release()
    cv2.destroyAllWindows()

def coordination(centroid, frame):
    width = frame.shape[1]
    intervel = (width * 10)/ 100
    local = 2
    centroid_left ,centroid_right = width/2 - intervel , width/2 + intervel
    if centroid[0] < centroid_left:
        local = 1
    elif centroid[0] > centroid_right:
        local = 3
    sendData(local)
    print("local: %d" % local)
def sendData(data):
    arduino.flush()
    temp = str(data)
    arduino.write(temp.encode("utf-8"))
    print("Send data to Arduino: "+temp)
    #time.sleep(10)
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    return array

def distance( p , q):
    return math.sqrt(sum((px - qx) ** 2.0 for px, qx in zip(p, q)))

def preprocess_face(face,required_size =(224,224)):

    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = np.asarray(image)

    return face_array

def get_dataset(path = "dataset/"):
    faces = []
    persons = []
    for name_img in os.listdir(path):
        person = name_img.split(".")[1]
        persons.append(person)
        face = cv2.imread(os.path.join(path,name_img))
        faces.append(face)

    return faces ,persons


def get_embedding(bboxfaces,model):
    faces = [preprocess_face(f) for f in bboxfaces]

    samples = np.asarray(faces,"float32")

    samples = preprocess_input(samples,version=2)    
    
    pred = model.predict(samples)

    return pred

    

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prototxt",default="MobileNetSSD_deploy.prototxt.txt",	help="path to Caffe 'deploy' prototxt file")
    ap.add_argument("-m", "--model", default="MobileNetSSD_deploy.caffemodel"	,help="path to Caffe pre-trained model")
    ap.add_argument("-c", "--confidence", type=float, default=0.5,	help="minimum probability to filter weak detections")
    ap.add_argument("-v", "--video_source", type=int, default=0,	help="video source (default = 0, external usually = 1)")
    args = vars(ap.parse_args())

    
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
    # create a Vgg face model vgg16, resnet50 , senet50
    model = VGGFace(model = "resnet50",include_top = False, input_shape = (224,224,3)) # 
    face_identify(model,net,args["confidence"])