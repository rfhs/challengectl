#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#main file

import os
import sys
# import datetime
import signal
import csv
from time import sleep
from random import randint, choice, shuffle
import random
import sqlite3
# from bottle import route, run, template, get, post, static_file
from multiprocessing import Process, Queue
import numpy as np
import subprocess
import string

from challenges import ask, cw, usb_tx, nbfm, spectrum_paint, pocsagtx_osmocom, lrs_pager, lrs_tx


def build_database(flagfile, devicefile):
    flag_input = read_flags(flagfile)
    flag_line = np.asarray(flag_input[1:])

    devices = read_devices(devicefile)

    conference = flag_input[0][0]
    conn = sqlite3.connect(conference + ".db")
    c = conn.cursor()
    c.execute('''CREATE TABLE flags(chal_id integer primary key,chal_name,flag,module,modopt1,modopt2,
    minwait integer,maxwait integer,freq1,freq2,freq3)''')
    c.execute("CREATE TABLE flag_status(chal_id integer primary key,enabled,lastrun integer,ready)")
    c.execute("CREATE TABLE devices(dev_id integer primary key,dev_string,dev_busy)")
    c.executemany("INSERT INTO flags VALUES (?,?,?,?,?,?,?,?,?,?,?)", flag_line)
    c.executemany("INSERT INTO flag_status VALUES (?,1,'',1)", flag_line[:, :1])
    c.executemany("INSERT INTO devices VALUES (?,?,0)", devices)
    conn.commit()
    conn.close()


class transmitter:
    # flag_args:chal_id,flag,modopt1,modopt2,minwait,maxwait,freq1

    def fire_ask(self, device_id, flag_q, device_q, *flag_args):
        print("\nTransmitting ASK\n")
        flag_args = flag_args[0]
        device = fetch_device(device_id)
        flag = flag_args[1]
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        # print("I ran fire_ask with flag=" + str(flag) + " and freq=" + str(freq))
        ask.main(flag.encode("utf-8").hex(), freq, device)
        sleep(3)
        device_q.put(device_id)
        sleep(randint(mintime, maxtime))
        flag_q.put(flag_args[0])

    def fire_cw(self, device_id, flag_q, device_q, *flag_args):
        print("\nTransmitting CW\n")
        flag_args = flag_args[0]
        device = fetch_device(device_id)
        print(device)
        flag = flag_args[1]
        speed = int(flag_args[2])
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        # print("I ran fire_cw with flag=" + str(flag) + " and freq=" +
        # str(freq) + " and speed=" + str(speed))
        p = Process(target=cw.main, args=(flag, speed, freq, device))
        p.start()
        p.join()
        sleep(3)
        device_q.put(device_id)
        sleep(randint(mintime, maxtime))
        flag_q.put(flag_args[0])

    # def fire_neutron(self, device_id, flag_q, device_q, *flag_args):
    #     print("\nTransmitting Neutron\n")
    #     flag_args = flag_args[0]
    #     device = fetch_device(device_id)
    #     flag = flag_args[1]
    #     speed = int(flag_args[2])
    #     freq = int(flag_args[6]) * 1000
    #     mintime = flag_args[4]
    #     maxtime = flag_args[5]
    #     # print("I ran fire_neutron with flag=" + str(flag) + " and freq=" +
    #     # str(freq) + " and speed=" + str(speed))
    #     p = Process(target=neutron.main, args=(flag.encode("utf-8").hex(), speed, freq, device))
    #     p.start()
    #     p.join()
    #     sleep(3)
    #     device_q.put(device_id)
    #     sleep(randint(mintime, maxtime))
    #     flag_q.put(flag_args[0])

    def fire_usb(self, device_id, flag_q, device_q, *flag_args):
        print("\nTransmitting USB\n")
        flag_args = flag_args[0]
        device = fetch_device(device_id)
        wav_src = str(flag_args[1])
        wav_rate = int(flag_args[2])
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        # print("I ran fire_usb with flag=" + str(wav_src) + " and freq=" +
        # str(freq) + " and wav_rate=" + str(wav_rate))
        usb_tx.main(wav_src, wav_rate, freq, device)
        sleep(3)
        device_q.put(device_id)
        sleep(randint(mintime, maxtime))
        flag_q.put(flag_args[0])

    def fire_nbfm(self, device_id, flag_q, device_q, *flag_args):
        print("\nTransmitting NBFM\n")
        flag_args = flag_args[0]
        device = fetch_device(device_id)
        wav_src = str(flag_args[1])
        wav_rate = int(flag_args[2])
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        # print("I ran fire_nbfm with flag=" + str(wav_src) + " and freq=" +
        # str(freq) + " and wav_rate=" + str(wav_rate))
        nbfm.main(wav_src, wav_rate, freq, device)
        sleep(3)
        device_q.put(device_id)
        sleep(randint(mintime, maxtime))
        flag_q.put(flag_args[0])

# def fire_dvbt():
#     dvbt_Q = Queue()
#     global conference
#     conn = sqlite3.connect(conference + ".db")
#     c = conn.cursor()
#     c.execute('''SELECT chal_id FROM flags WHERE module="dvbt"''')
#     flag_list = c.fetchall()
#     for row in flag_list:
#         dvbt_Q.put(row[0])
#
#     while True:
#         chal_id = dvbt_Q.get()
#         c.execute('''SELECT module,chal_id,flag,modopt1,modopt2,minwait,maxwait,
#         freq1 FROM flags WHERE chal_id=?''', (chal_id,))
#         current_chal = c.fetchone()
#         current_chal = list(current_chal)
#         try:
#             freq = int(current_chal[7]) * 1000
#         except ValueError:
#             if current_chal[7] == dvbt_rand:
#                 freq = select_dvbt("dvbt_" + str(randint(34, 69))) * 1000
#             else:
#                 freq = select_dvbt(current_chal[7])
#         flag1 = str(current_chal[2])
#         flag2 = str(current_chal[3])
#         dev = "0"
#         #send-movie.sh flag1 flag2 dev freq
#         send_movie = "sh ./challenges/send-movie.sh " + flag1 + flag2 + dev + str(freq)
#         os.system(send_movie)
#         sleep(60)
#         dvbt_Q.put(current_chal[1])

    def fire_pocsag(self, device_id, flag_q, device_q, *flag_args):
        print("\nTransmitting POCSAG\n")
        flag_args = flag_args[0]
        device = fetch_device(device_id)
        # Parse options from flag_args
        flag = flag_args[1]
        modopt1 = flag_args[2]
        mintime = flag_args[4]
        maxtime = flag_args[5]
        freq = int(flag_args[6]) * 1000
        # Configure options specific to pocsagtx_osmocom script
        pocsagopts = pocsagtx_osmocom.argument_parser().parse_args('')
        pocsagopts.deviceargs = "hackrf=0"
        pocsagopts.samp_rate = 1000000.0
        pocsagopts.pagerfreq = freq
        pocsagopts.capcode = int(modopt1)
        pocsagopts.message = flag
        # Call main in pocsagtx_osmocom, passing in pocsagopts options array
        pocsagtx_osmocom.main(options=pocsagopts)
        sleep(3)
        device_q.put(device_id)
        sleep(randint(mintime, maxtime))
        flag_q.put(flag_args[0])

    def fire_lrs(self, device_id, flag_q, device_q, *flag_args):
        print("\nTransmitting LRS\n")
        flag_args = flag_args[0]
        device = fetch_device(device_id)
        # Parse options from flag_args
        # For LRS, flag will be used to pass in the raw string of command args
        flag = flag_args[1]
        # modopt1 = flag_args[2]
        mintime = flag_args[4]
        maxtime = flag_args[5]
        freq = int(flag_args[6]) * 1000
        # Configure options specific to lrs_pager script
        lrspageropts = lrs_pager.argument_parser().parse_args(flag.split())
        # Generate pager.bin file
        # Generate random filename in /tmp/ for pager bin file
        randomstring = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        outfile = "/tmp/lrs_{}.bin".format(randomstring)
        lrspageropts.outputfile = outfile
        lrs_pager.main(options=lrspageropts)

        # Configure options specific to lrs_tx script
        lrsopts = lrs_tx.argument_parser().parse_args('')
        lrsopts.deviceargs = device
        lrsopts.freq = freq
        lrsopts.binfile = outfile
        # Gains below are defaults, added in case they need to be changed
        # lrsopts.bbgain = 20.0
        # lrsopts.ifgain = 20.0
        # lrsopts.rfgain = 47.0

        # Call main in pocsagtx_osmocom, passing in lrsopts options array
        lrs_tx.main(options=lrsopts)
        sleep(3)
        # Delete pager bin file from /tmp/
        os.remove(outfile)
        device_q.put(device_id)
        sleep(randint(mintime, maxtime))
        flag_q.put(flag_args[0])


def select_freq(band):
    with open("frequencies.txt") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == band:
                freq = randint(int(row[1]), int(row[2]))
                return((freq, row[1], row[2]))


def select_dvbt(channel):
    with open("dvbt_channels.txt") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == channel:
                return(int(row[1]))


def read_flags(flags_file):
    flag_input = []
    with open(flags_file) as f:
        reader = csv.reader(f)
        for row in reader:
            flag_input.append(row)
    return flag_input


def read_devices(devices_file):
    devices_input = []
    with open(devices_file) as f:
        reader = csv.reader(f, quotechar='"')
        for row in reader:
            devices_input.append(row)
    return devices_input


def fetch_device(dev_id):
    global conference
    conn = sqlite3.connect(conference + ".db")
    c = conn.cursor()
    c.execute("SELECT dev_string FROM devices WHERE dev_id=?", (dev_id,))
    device = c.fetchone()
    conn.close()
    return device[0]


# @get('/')
# def index_html():
#     global conference
#     return template('index.tpl', {'conference': conference})
#
#
# @get('/flag_manager')
# def flag_mgr():
#     return template('flag_manager.tpl')
#
#
# @route('/static/<filepath:path>', name='static')
# def server_static(filepath):
#     return static_file(filepath, root='./static')


def main(flagfile, devicefile):
    global conference
    device_Q = Queue()
    flag_Q = Queue()
    flag_input = read_flags(flagfile)
    conference = flag_input[0][0]
    if not os.path.exists(conference + ".db"):
        build_database(flagfile, devicefile)
    conn = sqlite3.connect(conference + ".db")
    c = conn.cursor()

    c.execute("SELECT dev_id FROM devices")
    dev_list = c.fetchall()
    for row in dev_list:
        device_Q.put(row[0])

    c.execute("SELECT chal_id FROM flag_status WHERE enabled=1")
    flag_list = c.fetchall()
    flag_list = list(sum(flag_list, ()))
    shuffle(flag_list)
    print(flag_list)
    for row in flag_list:
        flag_Q.put(row)

    dev_available = device_Q.get()
    t = transmitter()

    # dvbtp = Process(target=fire_dvbt)
    # dvbtp.start()
    try:
        while dev_available != None:
            chal_id = flag_Q.get()
            c.execute('''SELECT module,chal_id,flag,modopt1,modopt2,minwait,maxwait,
            freq1,chal_name FROM flags WHERE chal_id=? AND module!="dvbt"''', (chal_id,))
            current_chal = c.fetchone()
            current_chal = list(current_chal)
            try:
                current_chal[7] = int(current_chal[7])
                freq_or_range = str(current_chal[7])
            except ValueError:
                freq_range = select_freq(current_chal[7])
                current_chal[7] = freq_range[0]
                freq_or_range = str(freq_range[1]) + "-" + str(freq_range[2])

            print(f"\nPainting Waterfall on {current_chal[7]}\n")
            # spectrum_paint.main(current_chal[7] * 1000, fetch_device(dev_available))
            p = Process(target=spectrum_paint.main, args=(current_chal[7] * 1000, fetch_device(dev_available)))  # , daemon=True)
            p.start()
            p.join()
            print(f"\nStarting {current_chal[8]} on {current_chal[7]}")
            p = Process(target=getattr(t, "fire_" + current_chal[0]), args=(dev_available, flag_Q, device_Q, current_chal[1:]))
            p.start()
            # #we need a way to know if p.start errored or not
            # os.system("echo " + freq_or_range + " > /run/shm/wctf_status/" + current_chal[8] + "_sdr")
            # os.system('''timeout 15 ssh -F /root/wctf/liludallasmultipass/ssh/config -oStrictHostKeyChecking=no -oConnectTimeout=10 -oPasswordAuthentication=no -n scoreboard echo ''' + freq_or_range + " > /run/shm/wctf_status/" + current_chal[8] + "_sdr")
            dev_available = device_Q.get()
            sleep(1)
    except KeyboardInterrupt:
        print("Trying to Exit!")
        try:
            p.terminate()
            p.join()
        except UnboundLocalError:
            pass
        finally:
            exit()
        #dvbtp.join()


# def sigterm_handler(signal, frame):
#     print('Killed')
#     os.kill(os.getpid(), signal.SIGTERM)
#
#
# signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    # run(host='localhost', port=8080)
    try:
        main(sys.argv[1], sys.argv[2])
    except IndexError:
        print("Usage:")
        print("challengectl.py [flags file] [device file]")
