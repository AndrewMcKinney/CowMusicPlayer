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

#time converstion constants
SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
MILLISECONDS_IN_SECOND = 1000

#this sets up some directory constants
ROOT = pathlib.Path().absolute()
MUSIC_FOLDER_NAME = "music_files"
MUSIC_STORAGE_JSON_PATH = ROOT / "music_storage.json"
MUSIC_FOLDER_PATH = ROOT / MUSIC_FOLDER_NAME
TEMP_FOLDER_PATH = ROOT / "temp"
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


def convertTimeToMilliseconds(time : str):
    if(time.count(":") == 1):
        time_split = time.split(":")
        minutes = int(time_split[0])
        seconds = (minutes * SECONDS_IN_MINUTE) + int(time_split[1])
        milliseconds = seconds * MILLISECONDS_IN_SECOND
        return milliseconds
    elif(time.count(":") == 2):
        time_split = time.split(":")
        hours = int(time_split[0])
        minutes = (hours * MINUTES_IN_HOUR) + int(time_split[1])
        seconds = (minutes * SECONDS_IN_MINUTE) + int(time_split[2])
        milliseconds = seconds * MILLISECONDS_IN_SECOND
        return milliseconds

def parseTracks(file, storage_dict):
    tracks = []
    while(True):
        line = file.readline()
        unchanged_line = line
        line = line.strip() #removes extra whitespace
        if(len(line) == 0 or line[0] == "#"):
            continue
        if(line == "end_tracks"):
            break
        
        line = line.replace(" - ", "-") #Gladius - 4:35 -> Gladius-4:35

        if(line.count("-") > 2 | line.count("-") < 1):
            raise Exception("Error in Parse tracks on ({0}) converted to ({1}) ".format(unchanged_line, line))

        line_split = line.split("-")
        track_dict = {}
        for i in range(0, len(line_split)):
            #grab first character of ith string
            if(line_split[i][0].isdigit()):
                #this must be a time
                timeMilliseconds = convertTimeToMilliseconds(line_split[i])
                if("begin" in track_dict):
                    track_dict['end'] = timeMilliseconds
                else:
                    track_dict['begin'] = timeMilliseconds
            else:
                #this is the name of the track
                track_dict['name'] = line_split[i]
        tracks.append(track_dict)
    return tracks

def addMusicTracks(storage_dict):
    hasFailedCount = 0
    yt = None
    youtubeLink = storage_dict['link']
    while (hasFailedCount < 3):
        try:
            yt = YouTube(youtubeLink) #this sometimes fails not sure why
            break
        except:
            print("Youtube download failed, trying again... (Attempt:{0})".format(hasFailedCount + 1))
            hasFailedCount += 1
            time.sleep(0.5)
    if( hasFailedCount >= 3):
        raise Exception("Youtube download failed with link: {0}".format(youtubeLink))

    #select the right stream
    stream = yt.streams.filter(only_audio=True, file_extension='mp4').asc()[0]
    #cuts off the .mp4 (windows will add this back anyway)
    song_name = None
    if('name' in storage_dict):
        song_name = storage_dict['name']
    else:
        song_name = stream.default_filename[:-4] + " - " 
    
    #check for duplicates
    tracks = storage_dict['tracks']
    allDuplicates = True
    for track in tracks:
        if(findSongIndex(song_name + track['name']) == None):
            allDuplicates = False
            break
    if(allDuplicates):
        print("Skipping {0} since it only contains duplicate tracks".format(song_name))
    print("adding all tracks from {0}".format(song_name))

    #download the mp4 file
    print("Downloading {0}, this a few minutes".format(song_name))
    stream.download(output_path = TEMP_FOLDER_PATH, filename = song_name)
    stream_location_path = TEMP_FOLDER_PATH / (song_name + '.mp4')
    fullAudio = AudioSegment.from_file(stream_location_path)

    music_storage_json = openMusicStorageJson()

    for i in range(0, len(tracks)):
        track = tracks[i]
        audioSeg = None
        if('end' in track):
            audioSeg = fullAudio[track['begin']: track['end']]
        else:
            #if this is not the last song
            if(i + 1 != len(tracks)):
                #the end of this song is the beginning of the next one
                audioSeg = fullAudio[track['begin'] : tracks[i + 1]['begin']]
            else:
                #This is the last song, so grab the audio until the end
                audioSeg = fullAudio[track['begin'] : ]
        track_location_path = MUSIC_FOLDER_PATH / (song_name + track['name'] + ".mp4")
        audioSeg.export( track_location_path, format = "mp4")
        song_dict = {}
        song_dict['name'] = song_name + track['name']
        song_dict['path'] = str(track_location_path)
        song_dict['collecitons'] = []
        song_dict['youtube_link'] = youtubeLink

        music_storage_json['songs'].append(song_dict)
        music_storage_json['numberOfSongs'] += 1

        print("added {0}".format(song_name + track['name']))

    saveMusicStorageJson(music_storage_json)

    print("all tracks from {0} successfully added".format(song_name))
    os.remove(stream_location_path)

def parseImport(file):
    line = ""
    storage_dict = {}
    while(True):
        line = file.readline()
        line = line.strip()
        if(len(line) == 0 or line[0] == "#"):
            continue

        if(line.find("=") >= 0 ):
            line_split = line.split('=')
            command_name = line_split[0]
            command_value = line_split[1]
            if(command_name == "name"):
                storage_dict['name'] = command_value
                continue
            if(command_name == 'link'):
                storage_dict['link'] = command_value
                break #link is going to be the last sent command
            #this was an invalid command
            raise Exception("Error in parseImport: {0} is an unknown command".format(command_name))

        if(line == "tracks:"):
            storage_dict['tracks'] = parseTracks(file, storage_dict)
            continue
    if(not ('tracks' in storage_dict)):
        if('name' in storage_dict):
            addMusicSingle(storage_dict['link'], storage_dict['name'])
        else:
            addMusicSingle(storage_dict['link'])
    else:
        #This youtube video has tracks
        addMusicTracks(storage_dict)

        

def parseImportFast(file):
    while(True):
        line = file.readline()
        line = line.strip()
        if(len(line) == 0 or line[0] == "#"):
            continue
        if(line == "end_import_fast"):
            break
        addMusicSingle(line)
        time.sleep(0.1)

            

def parseMusicFile(fileName):
    with open(ROOT / fileName) as file:
        #0 is the offset, 2 means from EOF
        file.seek(0,2)
        EOF = file.tell()
        file.seek(0,0)

        while(True):
            line = file.readline()
            line = line.strip()

            if(file.tell() == EOF):
                break

            #empty lines and comments are skipped
            if(len(line) == 0 or line[0] == "#"):
                continue

            if(line == "import:"):
                parseImport(file)

            if(line == "import_fast:"):
                parseImportFast(file)

def deleteSong(song_name : str):
    print("you want to delete {0}".format(song_name))
    command = input("enter (confirm) to confirm")
    if(command == 'confirm'):
        print('deleting {0}'.format(song_name))
        songIndex = findSongIndex(song_name)
        if(songIndex == None):
            print("Error in deleteSong: {0} does not exist".format(song_name))
        music_json = openMusicStorageJson()
        songs = music_json['songs']
        os.remove(songs[songIndex]['path'])
        songs.pop(songIndex)
        music_json['songs'] = songs
        saveMusicStorageJson(music_json)
        print('{0} deleted'.format(song_name))
    else:
        print('deletion aborted')


def quickPlay(seg : AudioSegment, length_to_play : int):
        playingSong = simpleaudio.play_buffer ( 
            seg.raw_data,
            num_channels =seg.channels,
            bytes_per_sample = seg.sample_width,
            sample_rate = seg.frame_rate
        )
        time.sleep(length_to_play)
        playingSong.stop()
        

def editSong(song_name:str):
    songIndex = findSongIndex(song_name)
    music_json = openMusicStorageJson()
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

                quickPlay(trimmedSong, 3)
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
                quickPlay(sample_to_play, 3)
                command = input("Sounded acceptable, (Y)es or (N)o?")
                if(command.lower() == "y"):
                    os.remove(path)
                    trimmedSong.export(path, format = "mp4")
                    break


            




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

def openMusicStorageJson():
    with open(MUSIC_STORAGE_JSON_PATH, 'r') as music_storage:
        return json.load(music_storage)

def saveMusicStorageJson(new_json):
    with open(MUSIC_STORAGE_JSON_PATH, 'w') as music_storage:
        json.dump(new_json, music_storage, indent=4)

#this is really inefficent, O(N) time, should be O(1) really
def findSongIndex(song_name):
    music_json = openMusicStorageJson()
    songs = music_json['songs']
    for x in range(0, len(songs)):
        song = songs[x]
        if (song['name'] == song_name):
            return x
    return None


def addMusicSingle(youtubeLink, selected_name = None):
    hasFailedCount = 0
    yt = None
    while (hasFailedCount < 3):
        try:
            yt = YouTube(youtubeLink) #this sometimes fails not sure why
            break
        except:
            print("Youtube download failed, trying again... (Attempt:{0})".format(hasFailedCount + 1))
            hasFailedCount += 1
            time.sleep(0.5)
    if( hasFailedCount >= 3):
        raise Exception("Youtube download failed with link: {0}".format(youtubeLink))

    #select the right stream
    stream = yt.streams.filter(only_audio=True, file_extension='mp4').asc()[0]
    #cuts off the .mp4 (windows will add this back anyway)
    song_name = None
    if(selected_name != None):
        song_name = selected_name
    else:
        song_name = stream.default_filename[:-4] 
    
    #check for duplicates
    if (findSongIndex(song_name) != None):
        print("Skipping Duplicate {0}".format(song_name))
        return
    print("Downloading {0}...".format(song_name))
    #download the mp4 file
    stream.download(output_path = MUSIC_FOLDER_PATH, filename = song_name)
    song_location_path = MUSIC_FOLDER_PATH / (song_name + '.mp4')
    #prepare the song entry for json storage
    song_dict = {}
    song_dict['name'] = song_name
    song_dict['path'] = str(song_location_path)
    song_dict['collecitons'] = []
    song_dict['youtube_link'] = youtubeLink

    music_storage_json = openMusicStorageJson()

    music_storage_json['songs'].append(song_dict)
    music_storage_json['numberOfSongs'] += 1

    saveMusicStorageJson(music_storage_json)

    print(song_name + " successfully added!")

def playMusicMenu():
    print("which music list would you like to play?")
    print("HAHA, none are implemented of course, so you just have to deal with the default")

    music_storage_json = openMusicStorageJson()
    command = ""
    
    last_song_played = -1
    while(command.lower() != "q"):
        #the user can delete songs while in pause menu, so this has to be reloaded everytime
        #CONERN: PERFORMANCE
        music_storage_json = openMusicStorageJson()
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
                addMusicSingle(input("enter your youtube link: "))
                another = input("Add another? (Y)es/ anything else quits")
        
        elif(selection.lower() == "f"):
            print("Downloading from a file is now Supported!!!!!")
            parseMusicFile(input("which file do you want to import from?"))
        elif(selection.lower() == "q"):
            print("Exiting to menu...")
        else:
            print("Invalid command")

def testing():
    music_json = openMusicStorageJson()
    songs = music_json['songs']
    #this is "i was the sun"
    song = songs[0]
    command = input("Enter how many Milliseconds to trim from the end")
    seg = AudioSegment.from_file(song['path'])
    seg_test = seg[:-int(command)] #should remove the last 10 seconds
    quickPlay(seg_test[-10000:], 10)

def mainMenu():
    selection = "Null"
    print("Hello, welcome to the Cow Audio Player main menu")
    while( selection.lower() != "q"):
        print("Options: (A)dd music, (P)lay music, (E)dit music, (Q)uit")
        selection = input("What would you like to do?")
        if(selection.lower() == "t"):
            testing()
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

mainMenu()