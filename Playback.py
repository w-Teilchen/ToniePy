#!/usr/bin/env python3

import csv
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import os
import pygame
from random import randrange
from time import sleep
#import sounddevice
import sys
import threading
import time
from datetime import datetime

shuffle = False


def GetTitles(card_id):
    print("Finding matching items in library...")
    print(card_id)
    list =[]
    card_name = str(card_id)[0:9]
    with open('/home/pi/ToniePy/Cards.csv') as csvfile:
        Titles = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in Titles:
            temp = str(row[0])[0:9]
            if card_name.find(temp) != -1:
                list.append(str(row[1]))
        
    print("%d matching entries found." % len(list))
    
    return list

def ReadCurrentChapter(first_chapter):
    filename, file_extension = os.path.splitext(first_chapter)
    filename += '.save'
    if(not os.path.isfile(filename)): # no save -> start from beginning
        return 0,0
    with open(filename) as file:
        chapter, time = [int(x) for x in next(file).split()] # read first line
    if time < 30: # start from beginning if stopped less than 30 s into the chapter
        time = 0
    else: # repeat the last 15 s
        time -= 15
    return chapter, time


def SaveCurrentChapter(first_chapter, current_chapter, start_time):
    filename, file_extension = os.path.splitext(first_chapter)
    filename += '.save'
    with open(filename,"w") as file:
        file.write("%d %d" % (current_chapter, start_time))

def StartPlaybackCard(card_id):
    print("Starting playback...")
    global shuffle
    playback_thread = threading.currentThread()
    list = GetTitles(card_id)
    if (len(list) == 0): # empty list -> exit function
        print("No matching items found...")
        return
    current_chapter, start_time = ReadCurrentChapter(list[0])
    next_chapter = current_chapter       # this is the chapter that is played next
    next_chapter_start_time = start_time # this is the time the next chapter is started at
    start_clock = time.time()
    while getattr(playback_thread, "do_run", True):
        if (shuffle):
            current_chapter = randrange(len(list))
        if (pygame.mixer.music.get_busy() == 0): # ready to play a new chapter
            current_chapter = next_chapter       # update current_chapter
            if (current_chapter >= len(list)):   # current_chapter not in list -> dont start current_chapter
                break;
            print("Trying to play %s"% list[current_chapter])
            start_clock = time.time()
            start_time  = next_chapter_start_time
            pygame.mixer.music.load(str(list[current_chapter]))
            pygame.mixer.music.play(1,start_time)
            sleep(10)
            next_chapter += 1              # switch to next chapter
            next_chapter_start_time = 0    # reset start time
    sleep(0.1)
          
    print("Ending playback...")
    pygame.mixer.music.stop()
    time_played = time.time() - start_clock
    if current_chapter < len(list) and not shuffle: # playback stopped by removing RFID card -> save current chapter and time
        SaveCurrentChapter(list[0], current_chapter, start_time + time_played)
    else:
        SaveCurrentChapter(list[0], 0, 0)



reader = SimpleMFRC522()
pygame.mixer.init()
current_card = 0
try:
#    devs = sounddevice.query_devices()
#    print(devs) # Shows current output and input as well with "<" abd ">" tokens
#    for dev in devs:
#        print(dev['name'])

    print("Hold a tag near the reader\n")
    playback_thread = threading.Thread()
    while True:
        card_id = None;
        for trial in range(0, 3): # try multiple times to read the RFID card
            card_id = reader.read_id_no_block()
            print(datetime.now().strftime("%H:%M:%S") + ":", card_id)
            if (card_id != None):
                break
            
        
        if (card_id != current_card): # different card found -> stop playback and reset current_card
            playback_thread.do_run = False
            current_card = None
            
        if (card_id != current_card): # new card found -> start playback and set current_card
            playback_thread = threading.Thread(target=StartPlaybackCard, args=(card_id,))
            playback_thread.start()
            current_card = card_id
        sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()

