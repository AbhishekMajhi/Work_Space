## main file
from take_picture import take_photos

from recognize_faces_utils import *
from take_picture import take_photos,process_images,clear_face_dir
import os
from fr_utils import img_to_encoding
from keras.models import model_from_json
from inception_blocks_v2 import*
from keras import backend as K
K.set_image_data_format('channels_first')
import numpy as np
import sys
import tensorflow as tf
np.set_printoptions(threshold=sys.maxsize)

# face recognition model load 
def load_face_vari_model(load_model = True):
    with open('data and models/model.json','r') as f:
        json = f.read()
    model = model_from_json(json)
    model.load_weights("data and models/nn4.small2.channel_first.h5")
    print("Model loaded!!")
    # check_dir()
    return model

# model = load_face_vari_model()
# print('create db')
database = {}
# database = create_db(model,img_to_encoding)  # building database
# print('db create com')

# it will take pictures for face recognition..
def take_input():
    try:
        imgs = take_photos()
        process_images(imgs) # it will process all the images and save them in 'faces' directory.
    except:
        print("Facing error while opening camera!!!!")
        return
# take_input()

# will return all taken photos.. 
mypath = './faces'   
def get_faces():
    
    # list all files and save them in 'f[]'
    f = []
    for (dirpath, dirnames, filenames) in os.walk(mypath):
        try:
            f.extend(filenames)
            break
        except:
            continue
    return f

# f = get_faces()
# update_db(database, "Bro", os.path.join(mypath,f[1]), model,img_to_encoding)

# will identify who is the person....
def identify_face(faces, model, database):
    # global data
    my_path = './faces'
    # data = {
    #     'min_dist':None,
    #     'identity':None
    # }
    # data = {'min_dist':0, 'identity':None}
    data = who_is_it(os.path.join(my_path,faces[2]), database,model,img_to_encoding)
    return data
# clear_face_dir()

#del modelsssssss

if __name__ == "__main__":
    model = load_face_vari_model()
    
    take_input()
    f = get_faces()
    val = get_img_encoding(database,"sir", os.path.join(mypath,f[1]),model,img_to_encoding)
    print(val)
    who_is_it(os.path.join(mypath,f[1]), database,model,img_to_encoding)
    # data = {'min_dist':0, 'identity':None}
    # identify_face(f,model,database)
    del model