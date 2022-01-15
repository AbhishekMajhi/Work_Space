################# For Linux ###############
######### Arch KDE  ##########
import os
import subprocess
import random
import webbrowser
from tts import speak
from datetime import datetime, date
# 1
def open_files():
    try:
        subprocess.Popen('dolphin',shell=False)
    except:
        speak('not found!!!')
        print('not found!!!')
# 2
def open_browser():
    try:
        subprocess.Popen('firefox')
    except:
        try:
            open_brave()
        except:
            speak("you suck!! can't find brave either.")
        speak("Moron you havenot installed firefox yet!!")
# 2.5
def browsers():
    speak("Which browser you want?")
    ip = input("Your ans: ")
    if ip.find("firefox") != -1: # It will return -1 if it fails
        subprocess.Popen(['firefox'])
    elif ip.find("brave") != -1:
        open_brave()
    elif ip.find("chrome"):
        try:
            subprocess.Popen("chrome")
        except:
            speak("chrome not found or can't lunch chrome")
    elif ip.find("opera") != -1:
        subprocess.Popen("opera")
    else:
        speak("Lunching browser of my choice..")
        try:
            subprocess.Popen(['firefox'])
        except:
            speak("Have it your way.")
    
# 3
def open_code():
    try:
        subprocess.Popen('code')
    except:
        speak("failde to open code")
        print("failde to open code")
# 4
def open_musicPlayer():
    try:
        subprocess.Popen("elisa", shell=False)
        # subprocess.Popen('/bin/lollypop')
        
    except:
        speak("Lollypop is installed!!")
        print("Lollypop is installed!!")
# 5
def show_backup_commands():
    subprocess.Popen("timeshift", shell=True)
# 6
def update_system():
    subprocess.call(["sudo", "apt", "update"])
# 7
def upgrade_system():
    subprocess.call(["sudo", "apt", "upgrade"])
# 8
def open_videoplayer():
    subprocess.Popen('vlc')
# 9
def restart_system():
    subprocess.Popen("reboot")
# 10
def poweroff_system():
    subprocess.Popen("shutdown")
# 11
def stop_shutdown():  # for lite version of Application
    subprocess.Popen(["shutdown -c"])
    speak("Warning! System will be shutdown in one minute. You can cancel it if you want.")
# 11.5 Cancel shutdown command
def cancel_shutdown(password):  # this function is for full version of program.
    # Put a while loop while calling this method
    if checkpassword():  # Implement it
        subprocess.Popen("shutdown -c")
        speak("Shutdown command is now revoked.")
        return
    else:
        speak("password doesnot match. Want to try again?")
        ip = input("yes/no?")
        if ip.find("yes") or ip.find("fine") != -1:
            return "yes"
        else:
            return "no"
# 12
def text_editor():
    ip = input("Which one you want?")
    speak(ip)
    if ip == "kate":
        try:
            subprocess.Popen('kate')
        except:
            speak("Kate Not found!!")
            
    elif ip == "gedit":
        try:
            subprocess.Popen('gedit')
        except:
            speak("Gedit Not found!!")
    elif ip == 'nano':
        try:
            subprocess.Popen('nano')
        except:
            speak("Nano Not found!!")
    else:
        speak(f"we don't have {ip}")

# 13
def python_workspace():
    subprocess.call(". dude/bin/activate", shell= True) # source doesnot works here so we used . (dot) here. 
    subprocess.call('jupyter notebook', shell= True)
    os.chdir('/home/ultimatedude/Documents/Galvin Dude/')
# 14
def open_terminal():
    try:
        subprocess.Popen('konsole')
    except:
        speak("konsole not found!!")
# 15
def open_systemMonitor():
    try:
        subprocess.Popen('htop', shell = True)
    except:
        speak("Htop not found \n Installing.....")
        print("Htop not found \n Installing.....")
        subprocess.call('sudo pacman -S htop', shell= True)
        speak('Done!!\n Opening Htop...')
        print('Done!!\n Opening Htop...')
        os.system('htop')
# 16
def open_camera():
    try:
        subprocess.Popen('cheese', shell = False)
    except:
        speak("camera application is not found!!")
        print("camera application is not found!!")
# 17
def system_install(package_name):
    try:
        subprocess.call(['sudo apt install {}'.format(package_name)], shell= True)
    except:
        speak('default installation candidate is not available \n check installation candidate list...')
        print('default installation candidate is not available \n check installation candidate list...')
# 18
def remove_junkFiles():
    subprocess.call('sudo apt autoremove', shell= True)
# 19
def open_brave():
    try:
        subprocess.call('/bin/brave', shell=False)
    except:
        speak('Brave Web Browser is not found!')
        print('Brave Web Browser is not found!')
        str = input('do you wanna install it!!')  # yes/no
        subprocess.call('sudo pacman -S brave', shell= True)
# 20 
def open_mail():
    try:
        webbrowser.open('https://accounts.google.com/signin/v2/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&service=mail&sacu=1&rip=1&flowName=GlifWebSignIn&flowEntry=ServiceLogin')
    except:
        speak("failed to lunch gmail.")
#21
def open_htop():
    subprocess.Popen('htop',shell = True)

# 22
def backup_system():
    try:
        subprocess.Popen(["sudo","timeshift --create"], shell=True)
        speak("Backup created sucessfully!")
    except:
        speak("failed to create snapshots.")

# 23  self-intro
def self_intro():
    speak("Name Alice.")
    speak("Created by The Primordial Dude")
    speak("I am a Linux AI Assistant")
    speak("I thank you for choosing me.")

# 24 Weather
def get_weather():
    speak("This function is not implemented yet.")

# 25 open settings
def open_settings():
    try:
        subprocess.Popen('systemsettings5')
    except:
        speak("Something went wrong while lunching system settings.")

# 26 Skype
def open_skype():
    try:
        webbrowser.open("https://www.skype.com/en/free-conference-call/")
    except:
        speak("failed to lunch skype")

# 27 Google Meet
def open_meet():
    try:
        webbrowser.open("https://meet.google.com/")
    except:
        speak("failed to lunch meet")

# 28 Delete user account
def delete_my_account():
    speak("This function has not implemented yet")

# 29 Joke
def tell_joke():
    speak("This function has not implemented yet")


# 30 Self Distruct
def selfDistruct():
    speak("The time has not come yet")

# 31 Exit Alice
def exit_alice():
    '''This function will include code to shutdown all the running process
    of Alice and release all the memory reserver by it.
    But for now I am putting a temp code just for to run test cases'''
    exit(1)

# 32 Sleep 
def sleep():
    speak("System will now put into sleep mode.")
    subprocess.Popen("systemctl suspend")

# 33 Hibernate
def hibernate(password):
    
    if checkpassword():
        speak("System will now put into hibernation mode")
        subprocess.call("systemctl hibernate")
    else:
        speak("password doesnot match. Want to try again?")
        ip = input("yes/no?")
        if ip.find("yes") or ip.find("fine") != -1:
            return "yes"
        else:
            return "no"

# 34 Gnoome Disk Utility
def open_gnomeDisk():
    speak("This function has not implemented yet.")

# 35 Current Time
def c_time():
    now = datetime.now()
    ctime = now.strftime("%I:%M%p")
    speak(ctime)
    # ctime = ctime.split(":")
    # speak(f"Its {ctime[0]} hours {ctime[1]} minutes and {ctime[2]} seconds")
def c_date():
    now  = datetime.now().strftime("%B %d, %Y")
    # now = str(now)
    speak(now)

# 36 Location
def c_location():
    speak("This function has not implemented yet.")





#### Testing Area #####

# open_settings()
# open_htop()






#### Extra implementations ###
'''
1. Cancel shutdown
2. Date

'''

