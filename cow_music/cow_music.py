import os
import pathlib
from pydub import AudioSegment
import simpleaudio
import time
import msvcrt
from cow_song import CowSong
from pytube import YouTube
from pydub import silence
import constants
import menu
import json
import random
# takes about 1 minute to download a 3 hr video
#converts time in the format HH:MM:SS or MM:SS to milliseconds
def convertTimeToMilliseconds(time : str):
    #just one ":" means the format is MM:SS
    if(time.count(":") == 1):
        #split into minutes and seconds
        time_split = time.split(":")
        minutes = int(time_split[0])
        #convert minutes to seconds and add in the seconds from input string
        seconds = (minutes * constants.SECONDS_IN_MINUTE) + int(time_split[1])
        milliseconds = seconds * constants.MILLISECONDS_IN_SECOND
        return milliseconds
    #two ":" means that the format HH:MM:SS
    elif(time.count(":") == 2):
        #split into hours, minutes and seconds
        time_split = time.split(":")
        #get hours from string
        hours = int(time_split[0])
        #convert hours to minutes and add the minutes from input string
        minutes = (hours * constants.MINUTES_IN_HOUR) + int(time_split[1])
        #convert minutes to seconds and add seconds from input string
        seconds = (minutes * constants.SECONDS_IN_MINUTE) + int(time_split[2])
        milliseconds = seconds * constants.MILLISECONDS_IN_SECOND
        return milliseconds
    else:
        raise Exception("Error converting time into milliseconds on input string {0} ".format(time))

#Parses tracks when added music from an input file
def parseTracks(file, storage_dict):
    tracks = []
    while(True):
        #this iterates line by line
        line = file.readline()
        unchanged_line = line
        line = line.strip()
        #if a comment or empty time, continue
        if(len(line) == 0 or line[0] == "#"):
            continue
        #end_tracks marks the end of the track list
        if(line == "end_tracks"):
            break
        #Better formating for split
        #Gladius - 4:35 -> Gladius-4:35
        line = line.replace(" - ", "-")
        if(line.count("-") != 2 and line.count("-") != 1):
            raise Exception("Error in Parse tracks on ({0}) converted to ({1}) ".format(unchanged_line, line))
        
        line_split = line.split("-")
        track_dict = {}
        #there are several possiblilies for parsing:
        #TIME - TIME - NAME
        #TIME - NAME - TIME
        #NAME - TIME - TIME
        #NAME - TIME
        #TIME - NAME
        #TODO:this loop will have undefined behavior if the track name starts with number
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

#removes silence from the beginning and end of an audio file
def strip_silence(audioSeg):
    #want to leave a little bit of silence at the beginning and end
    #trim from the front
    #if preformance is an issue, code around 
    trim_ms = silence.detect_leading_silence(audioSeg)
    if(trim_ms > 100):
        audioSeg = audioSeg[trim_ms - 100 :]
    audioSeg = audioSeg.reverse()
    #trim from the end
    trim_ms = silence.detect_leading_silence(audioSeg)
    if(trim_ms > 100):
        audioSeg = audioSeg[trim_ms - 100 :]
    return audioSeg.reverse()

#adds multiple different user-defined tracks from a single youtube video
def addMusicTracks(storage_dict):

    hasFailedCount = 0
    yt = None
    youtubeLink = storage_dict['link']
    while (hasFailedCount < 3):
        try:
            #this connection can fail on occasion
            yt = YouTube(youtubeLink) 
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
    tracks_length = len(tracks)
    for x in range(0, tracks_length):
        track = tracks[tracks_length-1-x]
        #just checking for existance here, findSongIndex will return None if song DNE
        if(findSongIndex(song_name + track['name'])):
            tracks.remove(track)
        
    if(len(tracks) == 0):
        print("Skipping {0} since it only contains duplicate tracks".format(song_name))
        return
    print("adding all tracks from {0}".format(song_name))

    #download the mp4 file
    print("Downloading {0}, this a few minutes".format(song_name))
    stream.download(output_path = constants.TEMP_FOLDER_PATH, filename = song_name)
    stream_location_path = constants.TEMP_FOLDER_PATH / (song_name + '.mp4')
    fullAudio = AudioSegment.from_file(stream_location_path)

    music_storage_json = openMusicStorageJson()

    for i in range(0, len(tracks)):
        track = tracks[i]
        audioSeg = None
        #the track definition provided an ending
        if('end' in track):
            audioSeg = fullAudio[track['begin']: track['end']]
        #the track definition did not imply an ending meaning the ending is implied
        else:
            #if this is not the last song
            if(i + 1 != len(tracks)):
                #the end of this song is the beginning of the next one
                audioSeg = fullAudio[track['begin'] : tracks[i + 1]['begin']]
            else:
                #This is the last song, so grab the audio until the end
                audioSeg = fullAudio[track['begin'] : ]
        track_location_path = constants.MUSIC_FOLDER_PATH / (song_name + track['name'] + ".mp4")
        #removes any extra silence from the beginnig or the end of the audioSegment
        audioSeg = strip_silence(audioSeg)
        #saves the audioSegment to the file system
        audioSeg.export( track_location_path, format = "mp4")
        #create a song definiton for json storage
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
#handles parsing after the keyword "import:"
def parseImport(file):
    line = ""
    storage_dict = {}
    while(True):
        line = file.readline()
        line = line.strip()
        #if an empty line or comment, then skip
        if(len(line) == 0 or line[0] == "#"):
            continue
        #import can expect some definitions
        #right now only name and link are supported
        if(line.find("=") >= 0 ):
            line_split = line.split('=')
            command_name = line_split[0]
            command_value = line_split[1]
            if(command_name == "name"):
                storage_dict['name'] = command_value
                continue
            #reading a link implies that the parsing of import is over
            if(command_name == 'link'):
                storage_dict['link'] = command_value
                break #link is going to be the last sent command
            #this was an invalid command
            raise Exception("Error in parseImport: {0} is an unknown command".format(command_name))
        #Seeing tracks means we have to parse tracks
        if(line == "tracks:"):
            storage_dict['tracks'] = parseTracks(file, storage_dict)
            continue
    #tracks was not used, so we are adding a single music file
    if(not ('tracks' in storage_dict)):
        if('name' in storage_dict):
            addMusicSingle(storage_dict['link'], storage_dict['name'])
        else:
            addMusicSingle(storage_dict['link'])
    else:
        #This youtube video has tracks
        addMusicTracks(storage_dict)
        
#parses everything after "import_fast"
def parseImportFast(file):
    while(True):
        line = file.readline()
        line = line.strip()
        #comments and empty lines are skipped
        if(len(line) == 0 or line[0] == "#"):
            continue
        if(line == "end_import_fast"):
            break
        addMusicSingle(line)
        #TODO: why is this here?, test removing
        time.sleep(0.1)

#main driver function of parsing import files
def parseMusicFile(fileName):
    with open(constants.ROOT / fileName) as file:
        #0 is the offset, 2 means from EOF
        #this is used to check if the file has ended, 
        #since file.readline() will just return an empty string at EOF
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

#quickly play an audiosegment for a brief time
def quickPlay(seg : AudioSegment, length_to_play : int):
        playingSong = simpleaudio.play_buffer ( 
            seg.raw_data,
            num_channels =seg.channels,
            bytes_per_sample = seg.sample_width,
            sample_rate = seg.frame_rate
        )
        time.sleep(length_to_play)
        playingSong.stop()
#TODO: go over both of the below functions for preformance concerns
#returns a dictionary based on the music_storage.json file    
def openMusicStorageJson():
    with open(constants.MUSIC_STORAGE_JSON_PATH, 'r') as music_storage:
        return json.load(music_storage)
#saves changes to the music storage.json file
def saveMusicStorageJson(new_json):
    with open(constants.MUSIC_STORAGE_JSON_PATH, 'w') as music_storage:
        json.dump(new_json, music_storage, indent=4)

#TODO:this is really inefficent, O(N) time, should be O(1) really
#finds and returns the index of a song in the songs[] array
def findSongIndex(song_name):
    music_json = openMusicStorageJson()
    songs = music_json['songs']
    for x in range(0, len(songs)):
        song = songs[x]
        if (song['name'] == song_name):
            return x
    return None

#adds a single music file from a youtube video link
def addMusicSingle(youtubeLink, selected_name = None):
    #TODO: wrap connecting to youtbe into it's own function
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
    stream.download(output_path = constants.MUSIC_FOLDER_PATH, filename = song_name)
    song_location_path = constants.MUSIC_FOLDER_PATH / (song_name + '.mp4')
    audioSeg = AudioSegment.from_file(song_location_path)
    audioSeg = strip_silence(audioSeg)
    audioSeg.export( song_location_path, format = "mp4")
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

    #here is where I would grab the right song IF I IMPLEMENTED IT
    #need me some JSON setup

#a testing function that can be called, not reccomented for actual use
def testing():
    pass


