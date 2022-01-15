#### Prototype......
import time
from fr_utils import img_to_encoding
from tts import speak
from Profiles import get_obj 
from recognizer import recognize_speech_from_mic
from DataBase import*
from take_picture import *
from init_utills import get_permission, check_admin
from recognize_faces import get_faces, identify_face,load_face_vari_model, take_input, get_img_encoding
#from Ultimate_Dude import record_audio,respond
import speech_recognition as sr




if __name__ == '__main__':
    print("loading....")
    model = load_face_vari_model()
    obj = get_obj()
    db, cur = load_db()
    
    ### Varification sec:::
    print('Taking pictures for varification...')
    clear_face_dir()
    try:
        take_input()
        faces = get_faces()
    except:
        print("facing error while taking photos...")
    
    
    
    print('recognizing....')
    # 1st it will recognize if the user is an existing user or not
    d = get_face_encodings(cur)
    # print("db type:",type(d))
    # print("db value:", d)
    name = identify_face(faces, model,d)   # function which will check if the user is an existing user or new user..
    
    # if val == False:
        
    #     print('Redirecting...')
    #val = true when its a existing user
    # val = false when its a new user


    '''testing area temp contents....'''
    # lets say val is false
    if name['identity'] == None:
        # Means new user
        speak('It seems you are not an existing user!')
        speak("we have to create an account of yours first!") 
        speak("Checking for the existing admin account first! ")

        temp = check_admin()   #return True or False

        # temp = True
        if temp == True:
            speak("You must have the Admin Permission to login this account")
            speak("Do you want to proceed")
            inp = input("Please Enter y / n :"+"\n")
            if inp == 'y':
                speak("Getting Admin Permission") 
                temp = get_permission() 

                if temp == True:
                    speak("Congrats! Lets Create Account")
                    pass 
                else:
                    speak("Permission Denied")
                exit(1)
            else:
                speak("Thankyou for joining us , Exitting")
                exit(1)
        else:
            speak("Lets create your Account")

        ######## Sec 1: Name  ########

        speak('would you mind telling me whats your name is?')
        # for now only say your name 
        while 1:
            
            r = sr.Recognizer()
            mic = sr.Microphone()
            name = recognize_speech_from_mic(r, mic)
            if name != None:
                break
        obj.set_name(name['out'])
        print(obj.get_name())
        ''' Improvements
        -> use nameed entity recognition to recognize only name..
        -> or in simple method use nltk to remove any stop words so you  can grab only name  in general case.. '''
        
        ####### Sec 2: Taking Image ########
        # speak('please put your face inside that green rectangle shown on the camera window and then press "s"')
        take_input()
        f = get_faces()
        # temp_face_db = {
        #     "name": obj.get_name()
        # }
        # database = {}
        my_path = './faces'
        name = obj.get_name()
        print("name:", name)
        val = get_img_encoding(name,os.path.join(my_path,f[1]),model,img_to_encoding)
        '''Improvements
        -> use a pretrained model to recognize if that image is off a woman or a men
        then we can use sir or madam'''
        obj.add_face(val)
        speak('Done!')

        ######  Sec 3: Age   ############
        speak('and your age?')
        while 1:
            r = sr.Recognizer()
            mic = sr.Microphone()
            age = recognize_speech_from_mic(r, mic)
            if name != None:
                break
        obj.set_age(age['out'])
        print(obj.get_age())

        # sec 4: Entertainment
        # print('scaning disk for music and videos.....')
        # # code
        # print('done...')
        # speak("do you want to create a playlist for you. Where you can save all your favorite stuffs.")
        # res = recognize_speech_from_mic(r, mic)
        # if 'yes' or 'yeah' in res:
        #     speak('what name you wanna give to it?')
        #     play = recognize_speech_from_mic(r, mic)
        #     obj.set_playlist(play)
        #     print(obj.get_playlist())
        # else:
        #     speak('No problem!')

        # sec 5: Email

        speak('Please provide your email address')
        email = input("Enter email: ")
        obj.set_email(email)
        print(obj.get_email())

        # sec 6: password
        
        while(obj.set_password() != True):
            
            obj.set_password()
        
        name = obj.get_name()
        face = get_faces()
        age = obj.get_age()
        face = obj.get_face()
        email = obj.get_email()
        password = obj.get_password()
        # playlist = obj.get_playlist()
        data = [(name,age, 'm', 'user',password,face)]

        insert_user(data, db, cur)
        speak('all set. Everything is ready for you.')  # speak
        del model
    else:
        del model
        speak('well come back {}'.format(name))


# r = sr.Recognizer()
# mic = sr.Microphone()

# database.to_csv('database.csv')
# records = fetch_all_users(cur)
# for i in records:
#     print(i)

# while 1:
#         data = recognize_speech_from_mic(r,mic)
#         print(data['out'])
#         if 'exit' in data['out']:
#             break
#         # if 'open music' in data['out']:
#         #     applications.open_musicPlayer()
#         # speak('see ya')
#         # continue
#         label = identify(data['out'],word_to_index,ultimate_galvin_model)  # it will return a lable which represent a command category.
#         print('processing....')
#         respond(label,data['out'])





