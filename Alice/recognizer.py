import speech_recognition as sr
from tts import speak
import applications


# def record_audio():
#     r = sr.Recognizer()  # creating Recognizer obj.

#     with sr.Microphone() as source:
#         print("listening...")
#         r.adjust_for_ambient_noise(source,duration=5)
#         r.pause_threshold = 1 # seconds of non-speaking audio before a phrase is considered complete
#         r.energy_threshold = 350 # Minimum audio energy considered for recording. Increase it to say loudly.
        
#         audio = r.listen(source)
#         print('pass')

#         try:
#             print('recognizing...')
#             voice_data = r.recognize_google(audio)
#             print("User:", voice_data)
            
#         except:
#             print("Sorry. I don't get it. Please say that again")
#             return 'error'
#     return voice_data

# while 1:
#     voice_data = record_audio()  # it will return what we said
#     if voice_data == 'error':
#         voice_data = record_audio()
#     print(voice_data)



########## Taking input from audio file #####################

# path = '/home/ultimatedude/Documents/Galvin Dude/Ultimate_Speaking_dude_Linux/output.wav'
# def record_audio():
#     recg = sr.Recognizer()
#     with sr.AudioFile(path) as source:
#         recg.adjust_for_ambient_noise(source,duration=1)
#         audio_file = recg.listen(source)

#         try:
#             text = recg.recognize_google_cloud(audio_file)
#             print(text)
#         except:
#             print('check your internet connectivity!')

# record_audio()

########################### Working code for Linix System ##################

def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
           successful
    "error":   `None` if no error occured, otherwise a string containing
           an error message if the API could not be reached or
           speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
           otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print('say..')
        audio = recognizer.listen(source)
    data = {
        'out':None
    }
    try:
        data['out'] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        speak("API unavailable")
    except sr.UnknownValueError:
        # speech was unintelligible
        speak("Unable to recognize speech")

    return data

r = sr.Recognizer()
mic = sr.Microphone()

## testing area....
if __name__ == '__main__':
    while 1:
        data = recognize_speech_from_mic(r,mic)
        print(data['out'])
        if 'exit' in data['out']:
            break
        if 'open music' in data['out']:
            applications.open_musicPlayer()
        speak('see ya')
        continue
            
        