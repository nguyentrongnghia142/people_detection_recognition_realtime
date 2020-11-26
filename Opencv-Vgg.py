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
from time import time
import imutils




def face_identify(modelvgg,net, thresh = 0.5):
    # class model net 
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat","bottle", "bus", "car", "cat", "chair", "cow", "diningtable","dog", "horse", "motorbike", "person", "pottedplant", "sheep",	"sofa", "train", "admonitory"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    # source Face 
    cascadePath = "haarcascade_frontalface_default.xml"
    facecascade = cv2.CascadeClassifier(cascadePath)
    # font 
    font = cv2.FONT_HERSHEY_SIMPLEX
    print("[INFO] starting video stream...")
    cam = cv2.VideoCapture(0)
    cam.set(3,640)
    cam.set(4,480)
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)
    # get face database
    fps = FPS().start()
    data_face ,persons = get_dataset()
    pred_dataset = get_embedding(data_face,model)

    while True:
        # get frame 
        ret , frame = cam.read()
        t0 = time()
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

        # if confidence > args["confidence"]:
          
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
                        else:
                            id = "unknown"
                        
                    cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)            

        cv2.imshow('Detection and FaceRecognition',frame) 
        print("Execution time: %.4f(s)" % (time() - t0))

        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break

        fps.update()

    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    cam.release()
    cv2.destroyAllWindows()



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
    ap.add_argument("-p", "--prototxt", required=True,	help="path to Caffe 'deploy' prototxt file")
    ap.add_argument("-m", "--model", required=True,	help="path to Caffe pre-trained model")
    ap.add_argument("-c", "--confidence", type=float, default=0.2,	help="minimum probability to filter weak detections")
    ap.add_argument("-v", "--video_source", type=int, default=0,	help="video source (default = 0, external usually = 1)")
    args = vars(ap.parse_args())

    
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
    # create a Vgg face model vgg16, resnet50 , senet50
    model = VGGFace(model = "resnet50",include_top = False, input_shape = (224,224,3)) # 
    face_identify(model,net)