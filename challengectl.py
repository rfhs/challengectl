#main file

import os
# import sys
import datetime
import csv
from time import sleep
from random import randint
import sqlite3
from bottle import route, run, template, get, post, static_file
from multiprocessing import Process
import numpy as np

from challenges import ask
from challenges import cw
from challenges import neutron
from challenges import usb_tx
from challenges import nbfm
#from challenges.automate_ft8 import run_cq

def build_database():
    global conference
    flag_input = read_flags("flags.txt")
    flag_line = np.asarray(flag_input[1:])

    devices = read_devices("devices.txt")

    conference = flag_input[0][0]
    conn = sqlite3.connect(conference + ".db")
    c = conn.cursor()
    c.execute("CREATE TABLE flags(chal_id integer primary key,flag,module,modopt1,modopt2,minwait integer,maxwait integer,freq1,freq2,freq3)")
    c.execute("CREATE TABLE flag_status(chal_id integer primary key,enabled,lastrun integer,ready)")
    c.execute("CREATE TABLE devices(dev_id integer primary key,dev_string,dev_busy)")
    c.executemany("INSERT INTO flags VALUES (?,?,?,?,?,?,?,?,?,?)", flag_line)
    c.executemany("INSERT INTO flag_status VALUES (?,1,'',1)", flag_line[:,:1])
    c.executemany("INSERT INTO devices VALUES (?,?,0)", devices)
    conn.commit()
    conn.close()

def fire_ask(flag, freq, device):
    p = Process(target=ask.main, args=(flag.encode("hex"), freq, device))
    p.start()
    p.join()

def fire_cw(flag, speed, freq, device):
    p = Process(target=cw.main, args=(flag, speed, freq, device))
    p.start()
    p.join()

def fire_neutron(flag, speed, freq, device):
    p = Process(target=neutron.main, args=(flag.encode("hex"), speed, freq, device))
    p.start()
    p.join()

def fire_usb(wav_src, wav_rate, frequency, device):
    p = Process(target=usb_tx.main, args=(wav_src, wav_rate, frequency, device))
    p.start()
    p.join()

def fire_nbfm(wav_src, wav_rate, frequency, device):
    p = Process(target=nbfm.main, args=(wav_src, wav_rate, frequency, device))
    p.start()
    p.join()

# def run_ft8_cq(flag):
#     p = Process(target=run_cq.main, args=(flag))
#     p.start()
#     p.join()

def read_flags(flags_file):
    flag_input = []
    with open(flags_file) as f:
        reader = csv.reader(f) # change contents to floats
        for row in reader: # each row is a list
            flag_input.append(row)
    return flag_input

def read_devices(devices_file):
    devices_input = []
    with open(devices_file) as f:
        reader = csv.reader(f) # change contents to floats
        for row in reader: # each row is a list
            devices_input.append(row)
    return devices_input

@get('/')
def index_html():
    global conference
    return template('index.tpl', {'conference': conference})

@get('/flag_manager')
def flag_mgr():
    return template('flag_manager.tpl')

@route('/static/<filepath:path>', name='static')
def server_static(filepath):
    return static_file(filepath, root='./static')

def main():
    global conference
    flag_input = read_flags("flags.txt")
    conference = flag_input[0][0]
    if not os.path.exists(conference + ".db"):
        build_database()
    run(host='localhost', port=8080)

if __name__ == '__main__':
    main()
