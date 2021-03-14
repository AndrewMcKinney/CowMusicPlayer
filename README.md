# CowMusicPlayer
Music player specialized in downloading and playing music from youtube.


#### Installation
install ffmpeg:
ffmpeg - https://ffmpeg.org/download.html#build-windows

All modules listed in /py_requirements.txt, which can be installed with "make install"

NOTE: if you get an error similar to "get_ytplayer_config: could not find match for config_patterns" Then you need to run
python -m pip install git+https://github.com/nficano/pytube
The above line will install a more recent version of pytube where this error is fixed


## Usage
CowMusicPlayer uses a command line interface. Upon launching the app with 'make start', you will be given 4 options
YOU HAVE TO RUN COW MUSIC PLAYER WITH ADMIN RIGHTS WHEN DOWNLOADING MUSIC


(A)dd music:
    can add music by youtube link or with an import file
(P)lay music:
    Starts playing music randomly from what is already installed
(E)dit music:
    currently unimplemented
(Q)uit:
    exits the program

Select any option by typing A,P,E, or Q (not case sensitive)

#### Add music
The add music menu allows you to add music into the Cow Music Player. There are two ways to do this:

from (Y)ouTube:
    Simply copy and paste the link the to youtube channel, the entire video will be added as one musical track.
from (F)ile:
    Parses an entire file and adds all tracks and songs according to the format which is specified under [Adding From File](#Adding-from-File)

Cow Music Player tries to not add duplicates, but I would not rely on that ability much yet.

#### Adding From File
There are two ways to import music from a inport file.

###### import_fast:
import_fast is meant for rapidly adding many different youtube links. import_fast starts with "import_fast" and ends with "end_import_fast"
Leaving out either of these will lead to errors.
Example:

import_fast:
#Dovakinn
https://youtu.be/UsnRQJxanVM

#meglobox main theme
https://youtu.be/YOmAVOGW5Ak

#last Stand Remix FTL
https://youtu.be/PeYJrOEnnF8

#song for denise orchestral
https://youtu.be/scqEMVtIm_k

end_import_fast

Lines that start with # are considered comments and are simply ignored. 
Lines that are blank are also ignored.
So the above is the same as:

import_fast:
https://youtu.be/UsnRQJxanVM
https://youtu.be/YOmAVOGW5Ak
https://youtu.be/PeYJrOEnnF8
https://youtu.be/scqEMVtIm_k
end_import_fast

###### import:

The other way of importing music is with import:. import: starts with a "import:" and ends with a "link=youtubeLinkGoesHere"
With import: you have the ability to to set the name of the song, or to select certain tracks to seperate songs from within one larger video

Example:
import:
#comments can also be added here
name=Domina - 
tracks:
#comments can be added here as well
00:00:00 - Gladius
00:05:31 - Little Aliens
00:08:24 - Mire
00:11:01 - Ruiner
00:14:52 - Domina
#just make sure comments are on their own line
00:17:42 - Crixus
00:20:27 - Boom (Jason) (Or Walking out of hell one step at a time)
00:23:27 - Spartacus
00:26:45 - Afraid - 29:23
end_tracks
link=https://youtu.be/JPtSNYSqwMQ

In this example, I am added several tracks from one large hour+ video. 
The name= parameter will be the name that is added to the beginning of all the tracks.
So the names of the tracks that are added in this example would be:
Domina - Gladius
Domina - Little Aliens
Domina - Mire
Domina - Ruiner
Domina - Domina
etc...

Make sure to start the tracks with "tracks:" and end them with "end_tracks"

The start time, name, and end time of a track can appear in any order. 
Cow music player will assume the first time listed for a track is the beginning and the second time listed is the end.
The end time of the track can also be ommitted, in which case the end of the track is assumed to be the beginning of the next song or the end of the video.

the "link=" supplies the link to the youtube video, and also ends the "import:"

#### Paying Music
While playing music you can:
(S)kip the current song
(P)ause menu: open the pause menu
(Q)uit: stop playing music

##### pause menu:
Within the pause menu you can
(E)dit the current or previous song
(D)elete the current or previous song

Editing the song within the pasue menu works as follows:
first you select which song you wish to edit (current or previous)
Currently, the only editing option is to shave off milliseconds from the beginning or end of a song.
So say a song starts, but the first 5 seconds is actually the last 5 seconds of the song before it in some long video, This editing menu is made to fix that.

### Useful things of note:
Cow Music player will automatically shave off silence from the beginning and end of songs
"make clean" will reset the music player, deleting all data
Make sure to use the "copy video URL" link and not the link in the address bar

Cow Music Player will work as long as you dont *try* to break it. If you try to break Cow Music Player by doing something Silly like deleting the same song twice, bad things will happen.

## formatting_helper
Typing out the tracks of various songs in a 3 hour long video is slow and annoying.
Copy and pasting the track list from the video description is faster, but often the description is not in the right format. Fixing the formating is slow and annoying.
The formatting_help folder is meant to help with that. 
invoking 'make format' will cause formatting_helper.py to format everything in format_me.txt and output it to formatted.txt

The issues is that youtube track descriptions have no standard, so the formatting helper had to be ultra-highly configurable. This came at the cost of user experience. Thus: to configure the formatting_helper, you must edit the python file directly. All of the important constants are listed in the beginning of the file. The comments within the file do a good job of explaining how the constants work.























