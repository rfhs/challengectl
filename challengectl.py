#main file

import os
# import sys
import datetime
import csv
from time import sleep
from random import randint
import sqlite3
from bottle import route, run, template, get, post, static_file
from multiprocessing import Process, Queue
import numpy as np

from challenges import ask
from challenges import cw
from challenges import neutron
from challenges import usb_tx
from challenges import nbfm
#from challenges.automate_ft8 import run_cq

def build_database():
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

def fire_ask(flag, freq, device, mintime, maxtime,
flag_id, device_id, flag_q, device_q):
    ask.main(flag.encode("hex"), freq, device)
    device_q.put(device_id)
    sleep(randint(mintime, maxtime))
    flag_q.put(flag_id)
    # p = Process(target=ask.main, args=(flag.encode("hex"), freq, device))
    # p.start()
    # p.join()

def fire_cw(flag, speed, freq, device, mintime, maxtime,
flag_id, device_id, flag_q, device_q):
    cw.main(flag, speed, freq, device)
    device_q.put(device_id)
    sleep(randint(mintime, maxtime))
    flag_q.put(flag_id)
    # p = Process(target=cw.main, args=(flag, speed, freq, device))
    # p.start()
    # p.join()

def fire_neutron(flag, speed, freq, device, mintime, maxtime,
flag_id, device_id, flag_q, device_q):
    neutron.main(flag.encode("hex"), speed, freq, device)
    device_q.put(device_id)
    sleep(randint(mintime, maxtime))
    flag_q.put(flag_id)
    # p = Process(target=neutron.main, args=(flag.encode("hex"), speed, freq, device))
    # p.start()
    # p.join()

def fire_usb(wav_src, wav_rate, frequency, device, mintime, maxtime,
flag_id, device_id, flag_q, device_q):
    usb_tx.main(wav_src, wav_rate, frequency, device)
    device_q.put(device_id)
    sleep(randint(mintime, maxtime))
    flag_q.put(flag_id)
    # p = Process(target=usb_tx.main, args=(wav_src, wav_rate, frequency, device))
    # p.start()
    # p.join()

def fire_nbfm(wav_src, wav_rate, frequency, device, mintime, maxtime,
flag_id, device_id, flag_q, device_q):
    nbfm.main(wav_src, wav_rate, frequency, device)
    device_q.put(device_id)
    sleep(randint(mintime, maxtime))
    flag_q.put(flag_id)
    # p = Process(target=nbfm.main, args=(wav_src, wav_rate, frequency, device))
    # p.start()
    # p.join()

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
    device_Q = Queue()
    flag_Q = Queue()
    flag_input = read_flags("flags.txt")
    conference = flag_input[0][0]
    if not os.path.exists(conference + ".db"):
        build_database()
    conn = sqlite3.connect(conference + ".db")
    c = conn.cursor()

    c.execute("SELECT dev_id FROM devices")
    dev_list = c.fetchall()
    for row in dev_list:
        device_Q.put(row[0])

    c.execute("SELECT chal_id FROM flag_status WHERE enabled=1")
    flag_list = c.fetchall()
    for row in flag_list:
        flag_Q.put(row[0])

    dev_available = device_Q.get()
    while dev_available != None:
        chal_id = flag_Q.get()
        c.execute("SELECT module,flag,modopt1,modopt2,minwait,maxwait,freq1 FROM flags WHERE chal_id=?", (chal_id,))
        current_chal = c.fetchone()
        print(current_chal)
        dev_available = device_Q.get()
        sleep(1)


if __name__ == '__main__':
    #run(host='localhost', port=8080)
    main()
