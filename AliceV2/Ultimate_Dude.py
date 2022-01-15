#Modules
import speech_recognition as sr
#from gtts import gTTS
#import playsound
from time import ctime
import time
import webbrowser
import sys
import os
import random
import wikipedia
#import pyttsx3
from tts import speak
from galvin import identify,load_requirments,free_res
# from Music import play
from recognizer import recognize_speech_from_mic
# from init import *


         


#Voice service:

def respond(cmd_label,vc):

    # for self-introduction
    if cmd_label == 5:
       speak("My name is Alice. sir!")
       
       
    
    if cmd_label == 15:
       speak(ctime())

    #For opening youtube
    elif 'youtube' in vc:
        # Create a URL
        url= 'https://www.youtube.com/'
        # now we have our url let's browse
        webbrowser.get().open(url)
        speak("here is what i found for"+ vc)
        
    
    elif cmd_label == 2:
        speak("sorry this service is not available yet.")

    # Finding the  loaction
    #if 'find location' in voice_data:
    #    location = record_audio('where you wants to go?')
    #    # Create a URL
    #    url= 'https://google.nl/maps/place/' + location + '/&amp;'
    #    # now we have our url let's browse
    #    webbrowser.get().open(url)
    #    speak("here is the location of " + location)

    # for exit the program
    elif cmd_label == 14:
        print("Exiting..")
        speak("see you soon. sir")
        free_res(word_to_index, index_to_word, word_to_vec_map)
        sys.exit()
    
    # playing music    
    elif cmd_label == 1:
        #play music
        speak('enjoy. sir')
        play()
    
    # Weather forcasting
    # elif cmd_label == 2:
    #     get_weather()

    # Open fav movie folder:
    # elif 'movie directory' or 'movie folder' in voice_data:
    #     dir = profile.get_dir
    #     os.
    else:
        # speak('sorry. There is no matching action.')
        pass


word_to_index, index_to_word, word_to_vec_map,ultimate_galvin_model = load_requirments()
time.sleep(1)
speak("How can I help you?")

## testing area....
if __name__ == '__main__':
    while 1:
        
        r = sr.Recognizer()
        mic = sr.Microphone()
        data = recognize_speech_from_mic(r,mic)
        print(data['out'])
        if 'exit' in data['out']:
            break
        # if 'open music' in data['out']:
        #     applications.open_musicPlayer()
        # speak('see ya')
        # continue
        label = identify(data['out'],word_to_index,ultimate_galvin_model)  # it will return a lable which represent a command category.
        print('processing....')
        respond(label,data['out'])

# while 1:
#     #print('listening....')
#     voice_data = record_audio()  # it will return what we said
#     # if voice_data == 'error':
#     #     voice_data = record_audio()
#     print(voice_data)
#     print('identifying....')
#     label = identify(voice_data,word_to_index,ultimate_galvin_model)  # it will return a lable which represent a command category.
#     print('processing....')
#     respond(label)
    
# commands:            labels:      status:
# what is your name     5           completed
# what time is it
# find location
# search
# Exit                  14          completed
# play music            1           completed
# open youtube          0           completed
# weather               2           on going....
# 
