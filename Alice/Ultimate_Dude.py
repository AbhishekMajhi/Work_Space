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
from Music import play
#Initilize the recognizer class



# 1. Taking audio with microphone
def record_audio():  # WE set it false because we its default

    r = sr.Recognizer()
    with sr.Microphone() as source:

        # Get whatever we say from microphone and print it in console
        r.adjust_for_ambient_noise(source,duration=5)
        audio = r.listen(source)
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)
            #print(voice_data)
        except sr.UnknownValueError:
            speak("Sorry, I can't get what you are saying!")
            record_audio()
        except sr.RequestError:
            speak("Sorry, my server is down now!")
        return voice_data


# 2. Taking audio with microphone

# def record_audio():
#     r = sr.Recognizer()  # creating Recognizer obj.

#     with sr.Microphone() as source:
#         print("listening...")
#         r.pause_threshold = 1 # seconds of non-speaking audio before a phrase is considered complete
#         r.energy_threshold = 250 # Minimum audio energy considered for recording. Increase it to say loudly.
#         audio = r.listen(source)
        

#     try:
#         print('recognizing...')
#         voice_data = r.recognize_google(audio, language= 'en-in')
#         print("User:", voice_data)
        
#     except Exception as e:
#         print("Sorry. I don't get it. Please say that again")
#         return 'error'
#     return voice_data



#Voice service:

def respond(cmd_label):

    # for self-introduction
    if cmd_label == 5:
       print(voice_data)
       speak("My name is Alice. sir!")
    
    if cmd_label == 15:
       speak(ctime())

    #For opening youtube
    elif cmd_label == 0:
        print(voice_data)
        # Create a URL
        url= 'https://www.youtube.com/'
        # now we have our url let's browse
        webbrowser.get().open(url)
        speak("here is what i found for"+ voice_data)

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
        print(voice_data)
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
        speak('sorry. There is on matching action defined by my creator.')
    

        

word_to_index, index_to_word, word_to_vec_map,ultimate_galvin_model = load_requirments()
time.sleep(1)
speak("How can I help you?")


while 1:
    #print('listening....')
    voice_data = record_audio()  # it will return what we said
    # if voice_data == 'error':
    #     voice_data = record_audio()
    print(voice_data)
    print('identifying....')
    label = identify(voice_data,word_to_index,ultimate_galvin_model)  # it will return a lable which represent a command category.
    print('processing....')
    respond(label)
    
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
