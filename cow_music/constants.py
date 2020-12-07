
import pathlib
import json
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