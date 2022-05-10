# import talkey
# import pyttsx3
from gtts import gTTS
import random
import subprocess
import playsound
import os
# 1. Our Speak function: Using espeak engine

# def speak(sentence):
#     tts = talkey.Talkey(preferred_factor = 70.0,engine_preference=['espeak'],  espeak ={
#             # Specify the engine options:
#             'options': {
#                 'enabled': True,
#             },

#             # Specify some default voice options
#             'defaults': {
#                     'words_per_minute': 150,
#                     'variant': 'f4',
#             },

#             # Here you specify language-specific voice options
#             # e.g. for english we prefer the mbrola en1 voice
#             'languages': {
#                 'en': {
#                     'voice': 'en',
#                     'words_per_minute': 150
#                 },
#             }
#         })

#     tts.speak(sentence)
#     print(sentence)

#speak('hello again')

# # 2. Our Speak function: Using GTTS engine

def speak(audio):
   tts = gTTS(text = audio, lang = 'en')

   ran = random.randint(1, 1000000)
   audio_file = 'audio-' + str(ran) + '.mp3'  # This gonna be our random file name for our audio file.
   # Save our file temporarly
   tts.save(audio_file)
   #Play the audio
   playsound.playsound(audio_file)
   # along with print what she speak
   print("Alice: ",audio)
   # remove the audio file
   os.remove(audio_file)


# 3. Our Speak function: using pyttsx3 engine

# engine = pyttsx3.init('sapi5')   # sapi5: Microsoft speech API
# voices = engine.getProperty('voices')
# #print(voices[0].id)
# engine.setProperty('voice', voices[0].id)  # setting our voice

# def speak(audio):
#     engine.say(audio)
#     engine.runAndWait()


############## For Linux Systsm ########################3
# engine = pyttsx3.init()
# def speak(audio):
    
#     engine.say(audio)
#     engine.setProperty('rate',90)  #120 words per minute
#     engine.setProperty('volume',0.9) 
#     engine.runAndWait()


if __name__ == "__main__":
    speak("There’s nothing quite as fun or as necessary as using a projector. Whether you’re a teacher using a projector in your classroom or setting up an outdoor movie night on the wall of your house, projectors are a great way to turn an average space up to 11.")
# #working like butter.....