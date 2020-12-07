import os
import pathlib
from pydub import AudioSegment
import simpleaudio
import time
import msvcrt
from cow_song import CowSong
from pytube import YouTube
from pydub import silence
import cow_music
import constants
import json
import random


def mainMenu():
    selection = "Null"
    print("Hello, welcome to the Cow Audio Player main menu")
    while( selection.lower() != "q"):
        print("Options: (A)dd music, (P)lay music, (E)dit music, (Q)uit")
        selection = input("What would you like to do?")
        if(selection.lower() == "t"):
            cow_music.testing()
            return
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


def addMusicMenu():
    print("what music would you like to add?")
    selection = ""
    while(selection.lower() != "q"):
        print("options: add from (Y)outube, add from (F)ile, (Q)uit to menu")
        selection = input("selection:")
        if(selection.lower() == "y"):
            another = 'y'
            while(another.lower() == 'y'):
                cow_music.addMusicSingle(input("enter your youtube link: "))
                another = input("Add another? (Y)es/ anything else quits")
        
        elif(selection.lower() == "f"):
            print("Downloading from a file is now Supported!!!!!")
            cow_music.parseMusicFile(input("which file do you want to import from?"))
        elif(selection.lower() == "q"):
            print("Exiting to menu...")
        else:
            print("Invalid command")

#TODO: make rename this to deleteSong -> calls delete Song
def deleteSong(song_name : str):
    print("you want to delete {0}".format(song_name))
    command = input("enter (confirm) to confirm")
    if(command == 'confirm'):
        print('deleting {0}'.format(song_name))
        songIndex = cow_music.findSongIndex(song_name)
        if(songIndex == None):
            print("Error in deleteSong: {0} does not exist".format(song_name))
        music_json = cow_music.openMusicStorageJson()
        songs = music_json['songs']
        os.remove(songs[songIndex]['path'])
        songs.pop(songIndex)
        music_json['songs'] = songs
        cow_music.saveMusicStorageJson(music_json)
        print('{0} deleted'.format(song_name))
    else:
        print('deletion aborted')

def playMusicMenu():
    print("which music list would you like to play?")
    print("HAHA, none are implemented of course, so you just have to deal with the default")

    music_storage_json = cow_music.openMusicStorageJson()
    command = ""
    
    last_song_played = -1
    while(command.lower() != "q"):
        #the user can delete songs while in pause menu, so this has to be reloaded everytime
        #CONERN: PERFORMANCE
        music_storage_json = cow_music.openMusicStorageJson()
        song_list = music_storage_json['songs']
        #range is inclusive
        random_song_index = 0
        while (True):
            random_song_index = random.randint(0, len(song_list) - 1)
            #loop until last song is not equal to the current song
            #also will pass if playlist has a length of 1 to avoid an infinite loop
            if ( random_song_index != last_song_played or len(song_list) == 1 ):
                break
        if(last_song_played == -1):
            command = playSong(song_list[random_song_index])
        else:
            command = playSong(song_list[random_song_index], song_list[last_song_played])
        last_song_played = random_song_index

def playSong(song_dict, previous_song = None):
    song = CowSong(song_dict['path'], song_dict['name'])
    command = ""
    song.play()
    print("Now playing {0}".format(song_dict['name']))
    while (song.isPlaying()): 
        #NOTE: user does not have to press enter for this to register a command
        if msvcrt.kbhit(): #there is a key press waiting to be taken in
            print("read loud and clear!")
            command = input("enter your command ((S)kip, (P)ause menu, (Q)uit):")
            if (command.lower() == "s"):
                song.stop()
                break
            elif (command.lower() == "p") :
                song.pause()
                pauseMenu(song_dict, previous_song)
                song.play()
            elif (command.lower() == "q"):
                song.stop()
                break
            else:
                print("invalid command")
        time.sleep(0.1)
    return command


def pauseMenu(current_song, previous_song): 
    while(True):
        print("Paused, options: (E)dit current or previous song, (D)elete current or previous song")
        command = input("Enter (P) to continue (P)laying")
        if(command.lower() == 'p'):
            break
        if(command.lower() == 'd'):
            command = input("Delete (C)urrent or (P)revious song?")
            if(command.lower() == 'c'):
                deleteSong(current_song['name'])
            elif(command.lower() == 'p'):
                deleteSong(previous_song['name'])
        if(command.lower() == 'e'):
            command = input("Edit (C)urrent or (P)revious song?")
            if(command.lower() == 'c'):
                editSong(current_song['name'])
            elif(command.lower() == 'p'):
                editSong(previous_song['name'])

def editSong(song_name:str):
    songIndex = cow_music.findSongIndex(song_name)
    music_json = cow_music.openMusicStorageJson()
    path = music_json['songs'][songIndex]['path']
    if (songIndex == None):
        print("Error: editSong passed invalid song name")
        return
    while(True):
        command = input("trim the (B)egining or (E)nd? Or (Q)uit back to previous menu")
        if(command.lower() == 'q'):
            break
        if(command.lower() == 'b'):
            originalSong = AudioSegment.from_file(path)
            while(True):
                #entering 0 here will result in a crash
                command = input("Enter how many Milliseconds to trim from the begining")
                trimmedSong = originalSong[int(command):]
                print("does this sound right?")
                time.sleep(1)

                cow_music.quickPlay(trimmedSong, 3)
                command = input("Sounded acceptable, (Y)es or (N)o?")
                if(command.lower() == "y"):
                    os.remove(path)
                    trimmedSong.export( path, format = "mp4")
                    break
        if(command.lower() == 'e'):
            originalSong = AudioSegment.from_file(path)
            while(True):
                #entering 0 here will result in a crash
                command = input("Enter how many Milliseconds to trim from the end")
                trimmedSong = originalSong[:-int(command)]
                print("does this sound right?")
                time.sleep(1)

                sample_to_play = trimmedSong[-4000:]
                cow_music.quickPlay(sample_to_play, 3)
                command = input("Sounded acceptable, (Y)es or (N)o?")
                if(command.lower() == "y"):
                    os.remove(path)
                    trimmedSong.export(path, format = "mp4")
                    break

mainMenu()
