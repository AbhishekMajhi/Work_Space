from recognizer import recognize_speech_from_mic,get_recognizer
from applications import *
from tts import speak
from Alice_Command_Similarity_Pytorch_V1 import similarity_score



# model, tokenizer = load_sentence_model()
r, mic = get_recognizer()
data = recognize_speech_from_mic(r,mic)  # here data is a dict object. which have key called "out" where voice are stored as value

_, label = similarity_score(data['out'])
print(label)


if label == 'intro':
    self_intro()
elif label == 'music':
    open_musicPlayer()
elif label == 'weather':
    get_weather()
elif label == 'browser':
    open_browser()
elif label == 'settings':
    open_settings()
elif label == 'skype':
    open_skype()
elif label == "meet":
    open_meet()
elif label == "text editor":
    text_editor()
elif label == "code":
    open_code()
elif label == "delete account":
    delete_my_account()
elif label == "joke":
    tell_joke()
elif label == "Self Distruct":
    selfDistruct()
elif label == "exit":
    exit(1)
elif label == "shutdown":
    poweroff_system()
elif label == "reboot":
    restart_system()
elif label == "stop shutdown":
    stop_shutdown()
elif label == "":
    pass
else:
    pass 
