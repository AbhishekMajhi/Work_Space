import pygame  # used to create video games. But we gonna use its sound part for our purpose.
import os
from tkinter.filedialog import askdirectory #it permit to select dir
import tkinter as tkr

# payer stracture.
music_player = tkr.Tk()
music_player.title('Music is Life')
music_player.geometry("450x350")

pygame.init()
pygame.mixer.init(frequency=44100)

# create a directory that prompts the user to choose the folder where the music files are listed.
# directory = askdirectory()
directory = '/media/ultimatedude/Entertainment/Songs'
songs = []
for (dirpath, dirnames, filenames) in os.walk(directory):
    try:
        songs.extend(filenames)
        break
    except:
        continue

play_list = tkr.Listbox(music_player, font='Inter',
bg='black', selectmode=tkr.SINGLE)

for item in songs:
    pos = 0
    play_list.insert(pos,item)
    pos += 1

pygame.init()
pygame.mixer.init(frequency=44100)

# fun to control music player
def play():
    
    pygame.mixer.music.load(play_list.get(tkr.ANCHOR))
    var.set(play_list.get(tkr.ACTIVE))
    pygame.mixer.music.play()

def stop():
    pygame.mixer.music.stop()
def pause():
    pygame.mixer.music.pause()
def unpause():
    pygame.mixer.music.unpause()


# creates buttons 
Button1 = tkr.Button(music_player, width=5, height=3, font="Inter", text="PLAY", command=play, bg="blue", fg="white")
Button2 = tkr.Button(music_player, width=5, height=3, font="Inter", text="STOP", command=stop, bg="red", fg="white")
Button3 = tkr.Button(music_player, width=5, height=3, font="Inter", text="PAUSE", command=pause, bg="purple", fg="white")
Button4 = tkr.Button(music_player, width=5, height=3, font="Inter", text="UNPAUSE", command=unpause, bg="orange", fg="white")

var = tkr.StringVar() 
song_title = tkr.Label(music_player, font="Inter", textvariable=var)

song_title.pack()
Button1.pack(fill="x")
Button2.pack(fill="x")
Button3.pack(fill="x")
Button4.pack(fill="x")
play_list.pack(fill="both", expand="yes")
music_player.mainloop()