import os
import subprocess
import random
import webbrowser
from tts import speak
# 1
def open_files():
    try:
        os.system('dolphin')
    except:
        speak('not found!!!')
        print('not found!!!')
# 2
def open_browser():
    try:
        os.system('firefox')
    except:
        speak("Moron you havenot installed firefox yet!!")
        print("Moron you havenot installed firefox yet!!")
# 3
def open_code():
    try:
        os.system('code')
    except:
        speak("failde to open code")
        print("failde to open code")
# 4
def open_musicPlayer():
    try:
        subprocess.Popen('/bin/lollypop')
        
    except:
        speak("Lollypop is installed!!")
        print("Lollypop is installed!!")
# 5
def open_timeshift():
    subprocess.Popen(["sudo", "timeshift-gtk"])
# 6
def update_system():
    subprocess.call(["sudo", "apt", "update"])
# 7
def upgrade_system():
    subprocess.call(["sudo", "apt", "upgrade"])
# 8
def open_videoplayer():
    os.system('vlc')
# 9
def restart_system():
    subprocess.Popen(["restart"])
# 10
def poweroff_system():
    subprocess.Popen(["shutdown"])
# 11
def stop_shutdown():
    subprocess.Popen(["shutdown -c"])
# 12
def text_editor():
    try:
        os.system('kate')
    except:
        speak("Kate Not found!!")
        print("Kate Not found!!")
# 13
def python_workspace():
    subprocess.call(". dude/bin/activate", shell= True) # source doesnot works here so we used . (dot) here. 
    subprocess.call('jupyter notebook', shell= True)
    os.chdir('/home/ultimatedude/Documents/Galvin Dude/')
# 14
def open_terminal():
    try:
        os.system('konsole')
    except:
        speak("konsole not found!!")
        print("konsole not found!!")
# 15
def open_systemMonitor():
    try:
        os.system('htop')
    except:
        speak("Htop not found \n Installing.....")
        print("Htop not found \n Installing.....")
        subprocess.call('sudo apt install htop', shell= True)
        speak('Done!!\n Opening Htop...')
        print('Done!!\n Opening Htop...')
        os.system('htop')
# 16
def open_camera():
    try:
        os.system('cheese')
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
        subprocess.call('/bin/brave-browser')
    except:
        speak('Brave Web Browser is not found!!')
        print('Brave Web Browser is not found!!')
        str = input('do you wanna install it!!')  # yes/no
        subprocess.call('sudo apt install brave-browser', shell= True)
# 20 
def open_mail():
    webbrowser.open('https://accounts.google.com/signin/v2/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&service=mail&sacu=1&rip=1&flowName=GlifWebSignIn&flowEntry=ServiceLogin')

def open_htop():
    subprocess.Popen('htop',shell = True)
    
def location():
    send_url = "http://api.ipstack.com/check?access_key=ccb2135c0cf1e0c2309e154a7935098f"
    geo_req = requests.get(send_url)
    geo_json = json.loads(geo_req.text)
    latitude = geo_json['latitude']
    longitude = geo_json['longitude']
    city = geo_json['city']
    print(city)

def weather():
    apiKey = "a29d50396e3c4e9150d0e3c85192dd3e"
    baseUrl = "https://api.openweathermap.org/data/2.5/weather?q="
    city = input("Enter Your city name : ")
    completeUrl = baseUrl + city + "&appid=" + apiKey

    responce = requests.get(completeUrl)
    data = responce.json()

    kelvin_temp = data["main"]["temp"]

    cel = kelvin_temp - 273.15
    speak("Temperature in" + city + "is" + cel)
    print("Temperature in" + city + "is" + cel)
    

    



