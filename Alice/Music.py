import random
import os

#n = random.randint(0,4)
#print(n)

music_dir = '/media/ultimatedude/Entertainment/Songs'
song = os.listdir(music_dir)
#print(song)

def play():
        
    shuffle_song = random.choice(song)
    print(shuffle_song)
    os.startfile(os.path.join(music_dir, shuffle_song))

play()
