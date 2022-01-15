from tts import speak
from time import ctime
import os
import pandas as pd
from recognizer import recognize_speech_from_mic

from DataBase import *

class Profile():
    # welcome message
    def __init__(self):
        pass

    # set your name
    def set_name(self,name):
        self.name = name
        
    # get name
    def get_name(self):
        return self.name
    
    # set your age
    def set_age(self, age):
        self.age = age

    # get your age
    def get_age(self):
        return self.age
        # Here also need improvement same filter like 
   
    # add your face here
    def add_face(self, vec):
        # code here
        self.face_vec = str(vec)

    # Get face_vec here
    def get_face(self):
        return self.face_vec

    # Set email
    def set_email(self, mail):
        self.mail = mail

    # Get email here
    def get_email(self):
        return self.mail
    
    # set password  (for exp purpose we are using this approach. But later we will provide final implementation) 
    def  set_password(self):
        speak('Now! please enter a password')
        pass1 = input("New password: ")
        speak('please conform the password')
        pass2 = input("Confirm password: ")
        if pass1 == pass2:
            self.password = pass1
            return True
        else:
            speak('passwords doesnot match! please try again!')
            return False

    # Get password  (for exp...)
    def get_password(self):
        return self.password
    
    # set user playlist
    def set_playlist(self, playlist_name):
        self.playlist_name = playlist_name

    # Get user playlist
    def get_playlist(self):
        return self.playlist_name

    # Add your music dir here
    def add_music_dir(self,path):
        #code
        self.path = path

    # Get your music dir here
    def get_music_dir(self):
        return self.path
    
    # Add your movies_dir here
    # Dude  of doing all of thses you can scan entire hard drive for any video or audio files.
    def set_movie_dir(self, path):
        speak('can you write your movie path here')
        # code
        self.path = path

    # Get your movie path here
    def get_movie_dir(self):
        return self.path
    
    def set_favourites(self, data):
        database[self.name].append(data)
        speak('{data} is added to your favorite'.format(self.get_name()))  # check for error here



# Obj creation
obj = Profile()


def get_obj():
    return obj

  
