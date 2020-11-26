import os
import pathlib
from pydub import AudioSegment
import simpleaudio
import time

class CowSong():

    def __init__(self, path: pathlib.Path, songName  ):
        self._audioSegment = AudioSegment.from_file(path)
        self._secondsLength = len(self._audioSegment) / 1000 #len(self.song) is in milliseconds so we convert to seconds
        self._name = songName
        self._playingSong = None
        self._wasPaused = False
        self._timeElapsed = 0

    def play(self):
        seg = self.audioSegment
        if(self._wasPaused):
            #grabs the rest of the song, skipping timeElapsed seconds
            seg = self.audioSegment[(self._timeElapsed * 1000):] #need to convert to milliseconds
            print("timeElapsed: {0}".format(self._timeElapsed))
        #so depending on how long this takes to go, song will either end too soon or too late
        self._playingSong = simpleaudio.play_buffer ( 
            seg.raw_data,
            num_channels =seg.channels,
            bytes_per_sample = seg.sample_width,
            sample_rate = seg.frame_rate
        )
        #for now ill start the timer after the above line, which may let songs run just a tad too long
        self._timeStarted = time.time()

    def stop(self):
        self._playingSong.stop()

    #I dont know if pause will ever work, but ill keep it here for now
    def pause(self):
        self._wasPaused = True
        #this is time since played this time around + the old total of time elapsed
        self._timeElapsed = (time.time() - self._timeStarted) + self._timeElapsed
        self.stop()
    
    #checks to see if the song has finished playing. Will still return true if song is paused
    def isPlaying(self):
        return self._playingSong.is_playing()
    
    @property
    def playingSong(self):
        return self._playingSong

    @property
    def name(self):
        return self._name

    @property
    def secondsLength(self):
        return self._secondsLength

    @property
    def audioSegment(self):
        return self._audioSegment



