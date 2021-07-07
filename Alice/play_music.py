from Music import play
import os
import random
import subprocess
import sys
from playsound import playsound

mypath = '/media/ultimatedude/Entertainment/Songs/'
f = []

for (dirpath, dirnames, filenames) in os.walk(mypath):
    try:
        f.extend(filenames)
        break
    except:
        continue

    
#print(len(f))
def music_player():
    #player = 'A:Songs\05 - Kabhi Na Kabhi To Miloge.mp3'
    
    file = random.choice(f)
    # os.system(file)
    file = file.strip()

    
    return file
    
    #subprocess.Popen(os.path.join(dirpath, file), shell= True)
    # subprocess.call((mypath+file).split(),shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

music_player()

file = music_player()


playsound(os.path.join(dirpath, file))