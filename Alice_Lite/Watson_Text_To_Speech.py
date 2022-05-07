API = "G96W29F_93kiyWWS-TG6iYSWW1-epneG9cdg3_xXng4O"
# REGION = "us-east"
URL = "https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/598f2afb-efca-401b-a704-b880739c2032"


#### choose voices
# https://cloud.ibm.com/docs/text-to-speech?topic=text-to-speech-voices

from playsound import playsound

## Authenticate
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# setup service 
auth = IAMAuthenticator(API)
# TTS service
tts = TextToSpeechV1(auth)
# set url
tts.set_service_url(URL)
# Convert a string into speech
# with open('./speech.mp3', 'wb') as a_file:
#     res = tts.synthesize("Hello Abhishek. We meet again.", accept = 'audio/mp3', voice = 'en-US_AllisonV3Voice').get_result()
#     a_file.write(res.content)

# Convert from a text file
# with open("speak_test.txt", 'r') as f:
#     text = f.readlines()

# text = [line.replace('\n', '') for line in text]
# text = ''.join(str(line) for line in text)
# print(text)
# with open('./speech.mp3', 'wb') as a_file:
#     res = tts.synthesize(text, accept = 'audio/mp3', voice = 'en-US_AllisonV3Voice').get_result()
#     a_file.write(res.content)


def speak(text):
    with open('./speech.mp3', 'wb') as a_file:
        res = tts.synthesize(text, accept = 'audio/mp3', voice = 'en-US_AllisonV3Voice').get_result()
        a_file.write(res.content)
    playsound('speech.mp3')


speak("My name is Alice and I am a Linux Voice Assistant created by Abhishek Majhi")
