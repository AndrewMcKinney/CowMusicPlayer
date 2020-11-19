import os
import pathlib
from pydub import AudioSegment
from pydub.playback import play

from pytube import YouTube
 # takes about 1 minute to download a 3 hr video
yt = YouTube('https://www.youtube.com/watch?v=2FiyAOa6Lk8')

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
play(sound)