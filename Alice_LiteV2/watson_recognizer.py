from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource 
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

url = "https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/2910d9c4-fcae-4668-86ce-de46402dd673"
api_key = "NvTK7TJJPKRcrlVwuKGB7MdWHxzi8oe_nrUXVNjKt9o9"

# Setup Service
authenticator = IAMAuthenticator(api_key)
stt = SpeechToTextV1(authenticator=authenticator)
stt.set_service_url(url)

def recognize(path):
    with open(path, 'rb') as f:
        res = stt.recognize(audio=f, content_type='audio/mp3').get_result()
    text = res['results'][0]['alternatives'][0]['transcript']
    return text

if __name__ == '__main__':
    file_path = 'speech.mp3'
    print(recognize(file_path))