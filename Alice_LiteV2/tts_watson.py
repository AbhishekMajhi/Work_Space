from playsound import playsound

# API and URL
API_KEY = "Put your API KEY"
URL = "put your url"

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
    Hi everyone how are you. It's been a long time.
    '''
    speak(text)


#### Admin check passed ####
