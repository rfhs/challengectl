#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# import sys
from multiprocessing import Process, Queue
import logging
import string
import argparse
from time import sleep
from random import randint, choice, shuffle
import random
import sqlite3
import csv
import yaml
# import numpy as np

from challenges import (ask, cw, nbfm, spectrum_paint, pocsagtx_osmocom, lrs_pager, lrs_tx,
                        freedv_tx, fhss_tx, ssb_tx)

logging.basicConfig(filename='challengectl.log',
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S')

modulation_parameters = {
    'ask': {
        'mandatory': [
            'flag',
            'frequency'
        ],
        'optional': [
            'min_delay',
            'max_delay'
        ]
    },
    'cw': {
       'mandatory': [
            'flag',
            'frequency',
            'speed'
        ],
        'optional': [
            'min_delay',
            'max_delay'
        ]
    }, 'nbfm': {
        'mandatory': [
            'flag',
            'frequency'
        ],
        'optional': [
            'min_delay',
            'max_delay',
            'wav_samplerate'
        ]
    }, 'ssb': {
        'mandatory': [
            'flag',
            'frequency',
            'mode'
        ],
        'optional': [
            'min_delay',
            'max_delay',
            'wav_samplerate'
        ]
    }, 'pocsag': {
        'mandatory': [
            'flag',
            'frequency',
            'capcode'
        ],
        'optional': [
            'min_delay',
            'max_delay'
        ]
    }, 'lrs': {
        'mandatory': [
            'flag',
            'frequency'
        ],
        'optional': [
            'min_delay',
            'max_delay'
        ]
    }, 'freedv':{
        'mandatory': [
            'flag',
            'frequency',
            'mode'
        ],
        'optional': [
            'min_delay',
            'max_delay',
            'wav_samplerate'
        ]
    }, 'fhss': {
        'mandatory': [
            'flag',
            'frequency',
            'seed',
            'hop_rate',
            'hop_time',
            'channel_spacing'
        ],
        'optional': [
            'min_delay',
            'max_delay',
            'wav_samplerate'
        ]
    }
}

# def build_database(flagfile, devicefile):
#     """Create sqlite database based on flags file and devices file.
#        Database file name will be based on
#        conference name extracted from first line of flags file."""
#     flag_input = read_flags(flagfile)
#     # Skip first line of flag_input where conference information is stored
#     # Add remaining lines to flag_line array
#     flag_line = np.asarray(flag_input[1:])

#     devices = read_devices(devicefile)

#     # Read name of conference from first line of flag file
#     conference = flag_input[0][0]
#     # Create sqlite database for conference and connect to the database
#     conn = sqlite3.connect(conference + ".db")
#     c = conn.cursor()
#     # Create database schema
#     c.execute('''CREATE TABLE flags(chal_id integer primary key,chal_name,flag,module,modopt1,modopt2,
#     minwait integer,maxwait integer,freq1,freq2,freq3)''')
#     c.execute(
#         "CREATE TABLE flag_status(chal_id integer primary key,enabled,lastrun integer,ready)")
#     c.execute("CREATE TABLE devices(dev_id integer primary key,dev_string,dev_busy)")
#     # Insert flags from flag_line array into database
#     c.executemany(
#         "INSERT INTO flags VALUES (?,?,?,?,?,?,?,?,?,?,?)", flag_line)
#     # Add flag status row for each flag, setting each flag to enabled, lastrun blank, ready
#     c.executemany("INSERT INTO flag_status VALUES (?,1,'',1)",
#                   flag_line[:, :1])
#     # Insert devices from devices array into database, set each device to not busy
#     c.executemany("INSERT INTO devices VALUES (?,?,0)", devices)
#     conn.commit()
#     conn.close()


class Radio:
    """TODO: Doc string here"""

    def __init__(self, properties: dict) -> None:
        pass

    def check_freqrange(self, frequency) -> bool:
        pass

    def set_device_string(self, model, name, bias_t) -> str:
        pass


class Challenge:
    '''
    Contains properies and functions related to individual challenges
    '''
    def __init__(self, properties: dict) -> None:
        self.properties = properties
        self.name:str = properties.get('name')
        if properties.get('enabled') is not None:
            self.enabled:bool = properties.get('enabled')
        else:
            True

    def check_modulation(self, requested_modulation: str) -> bool:
        '''
        Checks if the modulation type is valid. Disables challenge if it's not.
        '''
        # Move this to another file
        # valid_modulation_types = ['ask', 'cw', 'nbfm', 'ssb', 'pocsag', 'lrs', 'freedv', 'fhss']
        valid_modulation_types = modulation_parameters.keys()
        if requested_modulation in valid_modulation_types:
            passed = True
            logging.info("Modulation check for %s passed.", self.name)
        else:
            logging.error("Unknown modulation type %s in %s", requested_modulation, self.name)
            self.enabled = False
            passed = False
        return passed

    # TODO: Finish this
    def check_parameters(self) -> None:
        '''
        Checks for manatory parameters
        Sets defaults for optional parameters
        '''
        if self.properties.get('flag') is not None:
            # Check if file exists
            self.flag = self.properties.get('flag')
            if not os.path.exists(self.flag):
                logging.error("File not found: %s", self.flag)
                self.enabled = False




# TODO: Maybe rename this to Flowgraph?
class transmitter:
    '''TODO: Doc string here'''
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

    # def fire_usb(self, device_id, flag_q, device_q, *flag_args):
    #     print("\nTransmitting USB\n")
    #     flag_args = flag_args[0]
    #     device = fetch_device(device_id)
    #     wav_src = str(flag_args[1])
    #     wav_rate = int(flag_args[2])
    #     freq = int(flag_args[6]) * 1000
    #     mintime = flag_args[4]
    #     maxtime = flag_args[5]
    #     # print("I ran fire_usb with flag=" + str(wav_src) + " and freq=" +
    #     # str(freq) + " and wav_rate=" + str(wav_rate))
    #     usb_tx.main(wav_src, wav_rate, freq, device)
    #     sleep(3)
    #     device_q.put(device_id)
    #     sleep(randint(mintime, maxtime))
    #     flag_q.put(flag_args[0])

    def fire_ssb(self, device_id, flag_q, device_q, *flag_args):
        """
        Call the ssb_tx flow graph to transmit Lower Sideband (LSB)
        or Upper Sideband (USB) modulated signals.
        """
        mode = 'tbd'
        print(f"\nTransmitting SSB ({mode})\n")
        flag_args = flag_args[0]
        device = fetch_device(device_id)
        wav_src = str(flag_args[1])
        wav_rate = int(flag_args[2])
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        # print("I ran fire_usb with flag=" + str(wav_src) + " and freq=" +
        # str(freq) + " and wav_rate=" + str(wav_rate))
        # TODO: Update the variables below.
        tx = ssb_tx.ssb_tx(audio_gain=0.6, bb_gain=20, dev=device,
                           freq=freq, if_gain=20, mode=mode, ppm=0,
                           rf_gain=20, rf_samp_rate=2000000,
                           wav_file=wav_src,
                           wav_samp_rate=wav_rate)
        tx.start()
        tx.wait()
        sleep(3)
        device_q.put(device_id)
        sleep(randint(mintime, maxtime))
        flag_q.put(flag_args[0])

    def fire_nbfm(self, device_id, flag_q, device_q, *flag_args):
        """
        Calls the nbfm flow graph to transmit Narrow Band FM modulated signals
        """
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
        # nbfm.main(wav_src, wav_rate, freq, device)
        # TODO: Update the variables below.
        tx = nbfm.nbfm(audio_gain=0.6, bb_gain=20, dev=device,
                       file=wav_src, freq=freq, if_gain=20,
                       ppm=0, rf_gain=20, rf_samp_rate=2000000, wav_rate=wav_rate)
        tx.start()
        tx.wait()
        sleep(3)
        device_q.put(device_id)
        sleep(randint(mintime, maxtime))
        flag_q.put(flag_args[0])

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
        pocsagopts.deviceargs = device
        pocsagopts.samp_rate = 2400000
        pocsagopts.pagerfreq = freq
        pocsagopts.capcode = int(modopt1)
        pocsagopts.message = flag
        # Call main in pocsagtx_osmocom, passing in pocsagopts options array
        pocsagtx_osmocom.main(options=pocsagopts)
        # pocsag_tx.main(flag, int(modopt1), freq, device)
        print("Finished TX POCSAG, sleeping for 3sec before returning device")
        sleep(3)
        # print("Slept for 30 seconds")
        device_q.put(device_id)
        # print("Returned Device top pool")
        sleep(randint(mintime, maxtime))
        # sleep(10)
        # print("Slept for 10 seconds")
        flag_q.put(flag_args[0])
        # print("Returned flag to pool")

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
        randomstring = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))
        outfile = f"/tmp/lrs_{randomstring}.bin"
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
        print("Removed outfile")
        device_q.put(device_id)
        print("Released Radio to pool")
        sleep(randint(mintime, maxtime))
        # sleep(10)
        print("Slept, returning flag to pool")
        flag_q.put(flag_args[0])
        print("Returned flag to pool")


def select_freq(band):
    """Read from frequencies text file, select row that starts with band argument.
    Returns tuple with randomly selected frequency, the minimum frequency for that band, and
    the maximum frequency for that band."""
    with open("frequencies.txt", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == band:
                freq = randint(int(row[1]), int(row[2]))
                return ((freq, row[1], row[2]))


# def select_dvbt(channel):
#     """TODO: Deprecate me"""
#     with open("dvbt_channels.txt") as f:
#         reader = csv.reader(f)
#         for row in reader:
#             if row[0] == channel:
#                 return (int(row[1]))


# def read_flags(flags_file):
#     """Read lines from flags_file and return a list of lists for each row in the flags_file.
#     The first item in the list contains conference information, and the remaining items in the
#     list contain information about each flag."""

#     flag_input = []
#     with open(flags_file) as f:
#         reader = csv.reader(f)
#         for row in reader:
#             flag_input.append(row)
#     return flag_input


# def read_devices(devices_file):
#     """Read lines from devices file, and return a list of lists for each row in the devices file."""
#     devices_input = []
#     with open(devices_file) as f:
#         reader = csv.reader(f, quotechar='"')
#         for row in reader:
#             devices_input.append(row)
#     return devices_input


# def fetch_device(dev_id):
#     """Query database for device string for a given device id and return the device string."""
#     global conference
#     conn = sqlite3.connect(conference + ".db")
#     c = conn.cursor()
#     c.execute("SELECT dev_string FROM devices WHERE dev_id=?", (dev_id,))
#     device = c.fetchone()
#     conn.close()
#     return device[0]


def argument_parser():
    parser = argparse.ArgumentParser(
        description="A script to run SDR challenges on multiple SDR devices.")
    # parser.add_argument('flagfile', help="Flags file")
    # parser.add_argument('devicefile', help="Devices file")
    parser.add_argument('configfile', help="YAML Configuration File", default='config.yml')
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def check_radios_config(radio_config):
    # check uniqueness of names
    # check freq limits
    # check sanity of gain values
    # check sanity of frequencies

    pass


def check_challenges(challenge_config):
    # check uniqeness of names
    # check modulation type
    # check options against modulator
    # check sanity of frequencies and other things that involve numbers
    pass


def parse_yaml(configfile) -> dict:
    '''
    Parse config.yml, check for mandatory fields
    '''
    parse_err = Exception('Cannot parse config file. Check log for more details')
    with open(configfile, 'r', encoding='utf-8') as conf_file:
        config = yaml.safe_load(conf_file)

    if config.get('radios') is not None:
        # radio_confg = config['radios']
        pass
    else:
        logging.critical("Section 'radios' is missing from configuration")
        raise parse_err

    if config.get('challenges') is not None:
        # challenge_config = config['challenges']
        pass
    else:
        logging.critical("Section 'challenges' is missing from configuration")
        raise parse_err

    return config



def main(options=None):
    if options is None:
        options = argument_parser().parse_args()

    args = options
    # Create thread safe FIFO queues for devices and flags
    device_Q = Queue()
    flag_Q = Queue()
    # Read flags file
    config = parse_yaml(args.configfile)
    # flag_input = read_flags(flagfile)
    # Extract conference name from first item returned by read_flags
    conference = config['conference']['name']
    # Check to see if database for conference name exists, create it if not
    # if not os.path.exists(conference + ".db"):
    #     build_database(flagfile, devicefile)
    # # Connect to conference database
    # conn = sqlite3.connect(conference + ".db")
    # c = conn.cursor()

    # Create a list of device IDs from devices in the database
    # c.execute("SELECT dev_id FROM devices")
    # dev_list = c.fetchall()

    dev_list = futurethinghere
    for row in dev_list:
        device_Q.put(row[0])

    # Create a list of challenge IDs based on flags that are enabled in the database
    # c.execute("SELECT chal_id FROM flag_status WHERE enabled=1")
    flag_list = config['challenges']
    flag_list = list(sum(flag_list, ()))
    # Randomize order of flag_list
    shuffle(flag_list)
    # logging.info(f'Initial flag transmision order: {flag_list}')
    # Put flag_list into thread safe flag_Q
    for row in flag_list:
        flag_Q.put(row)

    dev_available = device_Q.get()
    t = transmitter()

    try:
        while dev_available is not None:
            chal_id = flag_Q.get()
            c.execute('''SELECT module,chal_id,flag,modopt1,modopt2,minwait,maxwait,
            freq1,chal_name FROM flags WHERE chal_id=? AND module!="dvbt"''', (chal_id,))
            current_chal = c.fetchone()
            current_chal = list(current_chal)

            # Parse database fields into named variables to avoid using list index in multiple places
            cc_module = current_chal[0]
            cc_id = current_chal[1]
            cc_flag = current_chal[2]
            cc_modopt1 = current_chal[3]
            cc_modopt2 = current_chal[4]
            cc_minwait = current_chal[5]
            cc_maxwait = current_chal[6]
            cc_freq1 = current_chal[7]
            cc_name = current_chal[8]

            try:
                txfreq = int(cc_freq1)
                freq_or_range = str(txfreq)
            except ValueError:
                freq_range = select_freq(cc_freq1)
                txfreq = freq_range[0]
                freq_or_range = str(freq_range[1]) + "-" + str(freq_range[2])

            print(f"\nPainting Waterfall on {txfreq}\n")
            # spectrum_paint.main(current_chal[7] * 1000, fetch_device(dev_available))
            p = Process(target=spectrum_paint.main, args=(
                txfreq * 1000, fetch_device(dev_available)))  # , daemon=True)
            p.start()
            p.join()
            print(f"\nStarting {cc_name} on {txfreq}")
            # Create list of challenge module arguments, using txfreq to allow setting random freq here instead of in the challenge module
            challengeargs = [cc_id, cc_flag, cc_modopt1,
                             cc_modopt2, cc_minwait, cc_maxwait, txfreq]
            p = Process(target=getattr(t, "fire_" + cc_module),
                        args=(dev_available, flag_Q, device_Q, challengeargs))
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


if __name__ == '__main__':
    main()
