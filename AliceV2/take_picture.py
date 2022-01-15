# util file
import numpy as np
import cv2
import random
import os
from tts import speak


height = 500
font = cv2.FONT_HERSHEY_SIMPLEX

def show_images(images):
    print("Showing images..")
    image = random.choice(images)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    cv2.imshow('Dude',image)
    if key & 0xFF == ord('q'):  # quit
        yield
    cv2.destroyAllWindows()

def process_images(raw_frames):
    #Thses images looks green like color so let's fix them
    images = []

    for i,frame in enumerate(raw_frames):
        #get the roi
        roi = frame[100+1:425-1, 180+1:530-1]
        roi = cv2.cvtColor(roi,cv2.COLOR_BGR2RGB)
        roi = cv2.resize(roi,(96,96))  # resizing our images
        #lets save then in a folder
        cv2.imwrite('./faces/{}.png'.format(i),cv2.cvtColor(roi,cv2.COLOR_BGR2RGB))
        images.append(roi)

    print("Process complet..")

def take_photos():
    cam = cv2.VideoCapture(0)
    raw_frames = []
    count = 0
    speak("face to the camera and press s to capture and q to quit")
    while True:      
        _,frame = cam.read()
        #flip the  frame
        frame = cv2.flip(frame,1)  #  1 means means flipping around y-axis. Negative value
        # Rescaling camera o/p
        aspect =  frame.shape[1] / float(frame.shape[0])
        res = int(aspect * height) # menas landscape orientation
        frame = cv2.resize(frame, (res,height))
        
        # Add rectangle
        cv2.rectangle(frame, (175,80),(533,425), (0,255,0),2)
        cv2.putText(frame,'{} picture saved!!'.format(count),(31,34), font, 1,(255,255,255),2)
        cv2.imshow('window', frame)
        # now quit camera if 'q' is pressed or save when 's' is pressed
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):  # quit
            break
        elif key & 0xFF == ord('s'):  #  save
            count += 1
            raw_frames.append(frame)
            # show the frame
    #         plt.imshow(frame)
    #         plt.show()
    
    cam.release()
    cv2.destroyAllWindows()
    return raw_frames

def clear_face_dir():
    path = './faces'
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))



if __name__ == '__main__':
    images = take_photos()
    print("No problem found!")
# imgs = process_images(images)
# show_images(imgs)
# clear_face_dir()
