import os
import pathlib
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio
import time

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
#time.sleep(10) pauses for 10 seconds, blocking
time.sleep(100) #if execution end then song playing does as well