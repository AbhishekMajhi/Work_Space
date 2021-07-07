#### Prototype......
from tts import speak
from Profiles import get_obj 
from recognizer import record_audio
from DataBase import get_database
#from Ultimate_Dude import record_audio,respond

obj = get_obj()

if __name__ == '__main__':

    ### Varification sec:::
    print('opening camera for varification...')
    print('recognizing....')
    # 1st it will recognize if the user is an existing user or not
    #val,name = recognize_face()   # function which will check if the user is an existing user or new user..
    val = False   # for exp...
    name = 'UltimateDude'   # for exp..
    if val == False:
        print('Not an existing user!')
        print('Redirecting...')
    #val = true when its a existing user
    # val = false when its a new user


    '''testing area temp contents....'''
    # lets say val is false
    if val != True:
        # Means new user
        speak("we have to create an accout of yours first!") 

        ## sec 1: Taking Image

        speak('please put your face inside that green rectangle shown on the camera window and then press "s"')
        # img = takePhoto()
        img_vec = [1,2,3,4,5]  # for exp..
        obj.add_face(img_vec)
        '''Improvements
        -> use a pretrained model to recognize if that image is off a woman or a men
        then we can use sir or madam'''
        speak('Done!')

        ## sec 2: Name

        speak('would you mind telling me whats your name is sir..')
        # for now only say your name 
        name = record_audio()
        obj.set_name(name)
        print(obj.get_name())
        ''' Improvements
        -> use nameed entity recognition to recognize only name..
        -> or in simple method use nltk to remove any stop words so you  can grab only name  in general case.. '''

        ## sec 3: Age
        speak('and your age?')
        age = record_audio()
        obj.set_age(age)
        print(obj.get_age())

        # sec 4: Entertainment
        print('scaning disk for music and videos.....')
        # code
        print('done...')
        speak("do you want to create a playlist for you. Where you can save all your favorite stuffs.")
        res = record_audio()
        if 'yes' or 'yah' in res:
            speak('what name you wanna give to it?')
            play = record_audio()
            obj.set_playlist(play)
            print(obj.get_playlist())
        else:
            speak('No problem!')

        # sec 5: Email

        speak('Please provide your email address')
        email = record_audio()
        obj.set_email(email)
        print(obj.get_email())

        # sec 6: password
        
        while(obj.set_password() != True):
            
            obj.set_password()
            
        speak('all set. Now you are ready to rock!')  # speak
    else:
        speak('well come back {}'.format(name))



name = obj.get_name()
age = obj.get_age()
face = obj.get_face()
email = obj.get_email()
password = obj.get_password()
playlist = obj.get_playlist()

database = get_database()

data = {'face': [1,2,3,4,5], 'name': name, 'age':age, 'email': email, 'password': password, 'playlist': playlist}

database = database.append(data, ignore_index= False)
database.to_csv('database.csv')
print(database)


