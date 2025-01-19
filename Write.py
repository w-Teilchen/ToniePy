from time import sleep
import sys
from mfrc522 import SimpleMFRC522
import pygame
import numbers
import RPi.GPIO as GPIO
from os import system, name 

GPIO.setwarnings(False)
reader = SimpleMFRC522()
pygame.init()
print("...........................\n\n")
try:
    while True:
        system('clear')
        print("\n\n\n\nHold a tag near the reader")
        id, text = reader.read()
        print("Detected Card ID: " + text)
        try:
            CardNumber = input('Choose a new card text: ')
            CardNumberStr = str(CardNumber)
            text="CARD:" + CardNumberStr.zfill(4)
            print("........................")
            print("New Card ID == " + text)
            print("........................")
            val = input("Write Card ID? Type yes: ") 
            if (val == "yes"):
                reader.write(text)
            else:
                print("Writing Aborted")
        except ValueError:
            print("That's not an int!")
            print("Writing Aborted")
        sleep(2)
except KeyboardInterrupt:
    print("Exiting....")
    #GPIO.cleanup()
    #raises
