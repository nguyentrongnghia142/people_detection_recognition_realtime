import matplotlib.pyplot as plt 
from PIL import Image
from numpy import asarray
from mtcnn.mtcnn import MTCNN 
from keras_vggface.vggface import VGGFace 
# import cv2
from scipy.spatial.distance import cosine
from keras_vggface.utils import preprocess_input

def extract_face(imgname,required_size =(224,224)):
    img = plt.imread(imgname)

    detector = MTCNN()

    results = detector.detect_faces(img)

    x1, y1, w , h = results[0]["box"]

    x2, y2 = x1 + w , y1 + h

    face = img[y1:y2,x1:x2]

    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = asarray(image)

    return face_array

# cv2.imwrite("face.png",img)
def get_embedding(filenames):
    faces = [extract_face(f) for f in filenames]

    samples = asarray(faces,"float32")

    samples = preprocess_input(samples,version=2)
    # create a Vgg face model 
    model = VGGFace(model = "resnet50",include_top = False) # , input_shape = (224,224,3)
    
    pred = model.predict(samples)

    return pred



def is_match(know_embed,candidate_embed,thresh = 0.5):
    score = cosine(know_embed,candidate_embed)

    if score > thresh:
        print("face is Not a Match (%.3f > %.3f)" %(score,thresh))
    else: 
        print("face is a Match (%0.3f <= %0.3f)" %(score,thresh))
    
# test two face

def campareface(filenames,thresh = 0.5):
    faces = []
    for name in filenames:
        face = plt.imread(name)
        image = Image.fromarray(face)
        image = image.resize((224,224))
        face_array = asarray(image)
        faces.append(face_array)

    samples = asarray(faces,"float32")

    samples = preprocess_input(samples,version=2)
    # create a Vgg face model 
    model = VGGFace(model = "resnet50",include_top = False) # , input_shape = (224,224,3)
    
    pred = model.predict(samples)

    score = cosine(pred[0],pred[1])
    if score > thresh:
        print("face is Not a Match (%.3f > %.3f)" %(score,thresh))
    else: 
        print("face is a Match (%0.3f <= %0.3f)" %(score,thresh))


if __name__ == "__main__":
    # campare face
    listface = ["dataset/User.Nghia.1.jpg","dataset/User.Trung.1.jpg"]   
    campareface(listface) 

    # Application MTCNN and VGG16

    # filenames = ["image/2020-11-22-144550.jpg","image/2020-11-22-154729.jpg"]

    # embed = get_embedding(filenames)

    # identify = embed[0]
    # print("Positive tests")
    # is_match(identify,embed[1])
    # print("Negative tests")
    # is_match(identify,embed[2])
