#main file

# import os
# import sys
# import datetime
from time import sleep
from random import randint
import sqlite3
import bottle
# import multiprocessing

from challenges import ask
from challenges import cw
from challenges import neutron
from challenges import usb_tx
from challenges import nbfm

def hexgen(flag):
    hex_flag = flag.encode("hex")
    return hex_flag

def main():
    device = "hackrf=717a1d"
    wav_src = "/home/corey/WCTF/challengectl/challenges/PSK31.wav"
    wav_rate = 48000
    frequency = 146550000

    nbfm.main(wav_src, wav_rate, frequency, device)
    sleep(3)
    usb_tx.main(wav_src, wav_rate, frequency, device)
    #neutron.main(hexgen("The quick brown fox jumps over the lazy dog."), 70, 146550000, device)
    #sleep(3)
    # ask.main(hexgen("The quick brown fox jumps over the lazy dog."), 146550000, device)
    # sleeptimer = randint(5,30)
    # print("sleeping for " + str(sleeptimer) + " seconds...\n")
    # sleep(sleeptimer)
    # cw.main("THIS IS A TEST OF THE WCTF BROADCASTING SYSTEM.", 75, 146550000, device)
if __name__ == '__main__':
    main()
