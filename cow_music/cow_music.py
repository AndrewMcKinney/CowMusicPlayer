import os
import pathlib
from pydub import AudioSegment
import simpleaudio
import time
import msvcrt
from cow_song import CowSong
from pytube import YouTube
import json
import random
 # takes about 1 minute to download a 3 hr video
""" HERE BE OLD CODE
hasFailedCount = 0
yt = None
while (hasFailedCount < 3):
    try:
        yt = YouTube('https://www.youtube.com/watch?v=2FiyAOa6Lk8') #this sometimes fails not sure why
        break
    except:
        print("Youtube download failed, trying again. (Attempt:{0})".format(hasFailedCount + 1))
        hasFailedCount += 1
#print(pathlib.Path().absolute())
"""
#this sets up some constants
ROOT = pathlib.Path().absolute()
MUSIC_FOLDER_NAME = "music_files"
MUSIC_STORAGE_JSON_PATH = ROOT / "music_storage.json"
MUSIC_FOLDER_PATH = ROOT / MUSIC_FOLDER_NAME
#check to see if the music folder exists if not, then create it
if(not MUSIC_FOLDER_PATH.exists()):
    MUSIC_FOLDER_PATH.mkdir()
#check to see if the music_storage.json file exists, if not, then create it
if(not MUSIC_STORAGE_JSON_PATH.exists()):
    json_storage = {}
    json_storage['songs'] = []
    json_storage['playLists'] = []
    json_storage['numberOfSongs'] = 0
    with open(MUSIC_STORAGE_JSON_PATH, 'w') as data_file:
        json.dump(json_storage, data_file, indent=4)

""" HERE BE OLD CODE
stream = yt.streams.filter(only_audio=True, file_extension='mp4').asc()[0]
song_name = stream.default_filename[:-4]
#will automatically skip existing files -- perhaps not, ill have to manually code that in

stream.download(output_path = MUSIC_FOLDER_PATH, filename = song_name)
#step 1: get the mp4 file

song_location_path = MUSIC_FOLDER_PATH / (song_name + '.mp4')
sound = CowSong(song_location_path, song_name)
sound.play()
#default setup for songs:
# dict = {
#   song_name = XXXXXXX,
#   song_path = XXXXXXXX,
#   collections = []
#   }
#len(sound) returns milliseconds
print("waiting for input")
#time.time() - startTime < (len(sound) / 1000 )
while sound.isPlaying(): 
    #NOTE: user does not have to press enter for this to register a command
    if msvcrt.kbhit(): #there is a key press waiting to be taken in
        print("read loud and clear!")
        s = input("enter your command (skip):")
        if (s == "skip"):
            break
        elif (s == "pause") :
            sound.pause()
            time.sleep(3)
            sound.play()
            #sound.stop()
        else:
            print("invalid command")
    time.sleep(1)
"""

def playSong(song_dict):
    song = CowSong(song_dict['song_path'], song_dict['song_name'])
    command = None
    song.play()
    print("Now playing {0}".format(song_dict['song_name']))
    while (song.isPlaying()): 
        #NOTE: user does not have to press enter for this to register a command
        if msvcrt.kbhit(): #there is a key press waiting to be taken in
            print("read loud and clear!")
            command = input("enter your command ((S)kip, (P)ause), ((Q)uit):")
            if (command.lower() == "s"):
                song.stop()
                break
            elif (command.lower() == "p") :
                song.pause()
                input("waiting for any input to continue")
                song.play()
            elif (command.lower() == "q"):
                song.stop()
                break
            else:
                print("invalid command")
        time.sleep(0.1)
    return command

def addMusicSingle():
    hasFailedCount = 0
    youtubeLink = input("enter your youtube link: ")
    yt = None
    while (hasFailedCount < 3):
        try:
            yt = YouTube(youtubeLink) #this sometimes fails not sure why
            break
        except:
            print("Youtube download failed, trying again... (Attempt:{0})".format(hasFailedCount + 1))
            hasFailedCount += 1
            time.sleep(3)
    if( hasFailedCount >= 3):
        raise Exception("Youtube download failed with link: {0}".format(youtubeLink))
    #select the right stream
    stream = yt.streams.filter(only_audio=True, file_extension='mp4').asc()[0]
    #cuts off the .mp4 (windows will add this back anyway)
    song_name = stream.default_filename[:-4] 
    #download the mp4 file
    stream.download(output_path = MUSIC_FOLDER_PATH, filename = song_name)
    song_location_path = MUSIC_FOLDER_PATH / (song_name + '.mp4')
    #prepare the song entry for json storage
    song_dict = {}
    song_dict['song_name'] = song_name
    song_dict['song_path'] = str(song_location_path)
    song_dict['collecitons'] = []

    music_storage_json = None
    with open(MUSIC_STORAGE_JSON_PATH, 'r') as music_storage:
        music_storage_json = json.load(music_storage)

    music_storage_json['songs'].append(song_dict)

    #dumps from music_storage_json into music storage
    with open(MUSIC_STORAGE_JSON_PATH, 'w') as music_storage:
        json.dump(music_storage_json, music_storage, indent=4)

    print(song_name + " successfully added!")



def playMusicMenu():
    print("which music list would you like to play?")
    print("HAHA, none are implemented of course, so you just have to deal with the default")

    music_storage_json = None
    with open(MUSIC_STORAGE_JSON_PATH, 'r') as music_storage:
        music_storage_json = json.load(music_storage)
    command = ""
    song_list = music_storage_json['songs']
    while(command.lower() != "q"):
        #range is inclusive
        random_song_index = random.randint(0, len(song_list) - 1)
        command = playSong(song_list[random_song_index])


    #here is where I would grab the right song IF I IMPLEMENTED IT
    #need me some JSON setup
def addMusicMenu():
    print("what music would you like to add?")
    selection = ""
    while(selection.lower() != "q"):
        print("options: add from (Y)outube, add from (F)ile, (Q)uit to menu")
        selection = input("selection:")
        if(selection.lower() == "y"):
            another = 'y'
            while(another.lower() == 'y'):
                addMusicSingle()
                another = input("Add another? (Y)es/ anything else quits")
        elif(selection.lower() == "f"):
            print("downloading from a file is not implemented yet!")
        elif(selection.lower() == "q"):
            print("Exiting to menu...")
        else:
            print("Invalid command")

def mainMenu():
    selection = "Null"
    print("Hello, welcome to the Cow Audio Player main menu")
    while( selection.lower() != "q"):
        print("Options: (A)dd music, (P)lay music, (E)dit music, (Q)uit")
        selection = input("What would you like to do?")
        if(selection.lower() == "a"):
            print("add music selected")
            addMusicMenu()
        elif (selection.lower() == "p"):
            playMusicMenu()
        elif (selection.lower() == "e"):
            print("edit music selected, this is not implemented")
        elif (selection.lower() == 'q'):
            print("quitting")
        else:
            print("invalid command")

mainMenu()