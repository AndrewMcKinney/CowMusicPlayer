import os
import pathlib
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio
import time
import msvcrt

from pytube import YouTube
 # takes about 1 minute to download a 3 hr video
yt = YouTube('https://www.youtube.com/watch?v=2FiyAOa6Lk8') #this sometimes fails not sure why

#print(pathlib.Path().absolute())

ROOT = pathlib.Path().absolute()
MUSIC_FOLDER_NAME = "music_files"
MUSIC_FOLDER_PATH = ROOT / MUSIC_FOLDER_NAME
if(not MUSIC_FOLDER_PATH.exists()):
    MUSIC_FOLDER_PATH.mkdir()
stream = yt.streams.filter(only_audio=True, file_extension='mp4').asc()[0]
song_name = stream.default_filename[:-4]
#will automatically skip existing files -- perhaps not, ill have to manually code that in

stream.download(output_path = MUSIC_FOLDER_PATH, filename = song_name)
#step 1: get the mp4 file

sound = AudioSegment.from_file( MUSIC_FOLDER_PATH / (song_name + '.mp4'))
#play(sound)
playing_song = simpleaudio.play_buffer ( 
    sound.raw_data,
    num_channels =sound.channels,
    bytes_per_sample = sound.sample_width,
    sample_rate = sound.frame_rate
)
startTime = time.time()
#len(sound) returns milliseconds
print("waiting for input")
while time.time() - startTime < (len(sound) / 1000 ): 
    #NOTE: user does not have to press enter for this to register a command
    if msvcrt.kbhit(): #there is a key press waiting to be taken in
        print("read loud and clear!")
        s = input("enter your command (skip):")
        if (s == "skip"):
            break
        elif (s == "print") :
            print("time value: {0}".format(time.time() - startTime))
            print("len value: {0}".format(len(sound) / 1000))
        else:
            print("invalid command")
    time.sleep(1)

#time.sleep(10) pauses for 10 seconds, blocking #if execution end then song playing does as well