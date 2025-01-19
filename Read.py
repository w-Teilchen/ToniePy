from time import sleep
import sys
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
from os import system, name 




reader = SimpleMFRC522()
system('clear')
try:
    while True:
        print("Hold a tag near the reader\n\n")
        id = reader.read_id()
        print("ID: %s" % id)
        print("..............")
        sleep(2)
except KeyboardInterrupt:
    GPIO.cleanup()
    raises