#main file

# import os
# import sys
import datetime
import csv
from time import sleep
from random import randint
import sqlite3
from bottle import route, run, template
from multiprocessing import Process

from challenges import ask
from challenges import cw
from challenges import neutron
from challenges import usb_tx
from challenges import nbfm

# def hexgen(flag):
#     hex_flag = flag.encode("hex")
#     return hex_flag

def fire_ask(flag, freq, device):
    #main.dev_busy = True
    p = Process(target=ask.main, args=(flag.encode("hex"), freq, device))
    p.start()
    p.join()

def fire_cw(flag, speed, freq, device):
    main.dev_busy = True
    p = Process(target=cw.main, args=(flag, speed, freq, device))
    p.start()
    p.join()

def fire_neutron(flag, speed, freq, device):
    main.dev_busy = True
    p = Process(target=neutron.main, args=(flag.encode("hex"), speed, freq, device))
    p.start()
    p.join()

def fire_usb(wav_src, wav_rate, frequency, device):
    main.dev_busy = True
    p = Process(target=usb_tx.main, args=(wav_src, wav_rate, frequency, device))
    p.start()
    p.join()

def fire_nbfm(wav_src, wav_rate, frequency, device):
    main.dev_busy = True
    p = Process(target=nbfm.main, args=(wav_src, wav_rate, frequency, device))
    p.start()
    p.join()

def read_flags(flags_file):
    flag_input = []
    with open(flags_file) as f:
        reader = csv.reader(f) # change contents to floats
        for row in reader: # each row is a list
            flag_input.append(row)
    return flag_input

@route('/hello')
def hello():
    return "Hello World!"

def main():
    flag_input = read_flags("flags.txt")

    conference = flag_input[0][0]
    conn = sqlite3.connect(conference + ".db")
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE flags(chal_id,enabled,flag,module,modopt1,modopt2,minwait,maxwait,lastrun,freq1,freq2,freq3)")
    except:
        pass

    c.executemany("INSERT INTO flags VALUES (?,1,?,?,?,?,?,?,'',?,?,?)", flag_input[1:])


    conn.commit()
    c.execute("SELECT * FROM flags")
    print(c.fetchall())
    device = "hackrf=717a1d"
    main.dev_busy = False
    # ask1_flag = "The quick brown fox jumps over the lazy dog."

    #run(host='localhost', port=8080, debug=True)

if __name__ == '__main__':
    main()
