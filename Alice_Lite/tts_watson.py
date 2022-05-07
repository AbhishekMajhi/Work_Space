from playsound import playsound

# API and URL
API_KEY = "G96W29F_93kiyWWS-TG6iYSWW1-epneG9cdg3_xXng4O"
URL = "https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/598f2afb-efca-401b-a704-b880739c2032"

## Authenticate
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# setup service 
auth = IAMAuthenticator(API_KEY)
# TTS service
tts = TextToSpeechV1(auth)
# set url
tts.set_service_url(URL)

# Choose voices from here.
# https://cloud.ibm.com/docs/text-to-speech?topic=text-to-speech-voices

def speak(text):
    with open('./speech.mp3', 'wb') as a_file:
        res = tts.synthesize(text, accept = 'audio/mp3', voice = 'en-US_AllisonV3Voice').get_result()
        a_file.write(res.content)
    playsound('speech.mp3')

if __name__ == '__main__':
    text = '''
    Hello there.. mister, I am Jeanne. I am here to make your linux uses easier. Don't expect
    anything more..
    '''
    speak(text)


#### Admin check passed ####