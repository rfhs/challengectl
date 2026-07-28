#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
from time import sleep
from random import randint, choice, shuffle
import random
import sqlite3
from multiprocessing import Process, Queue
import numpy as np
import string
import argparse
import subprocess
import math
import json

from challenges import ask, cw, usb_tx, nbfm, spectrum_paint, pocsagtx_osmocom, lrs_pager, lrs_tx
from challenges.gotenna import gotenna_pro_tx_bladerf, gotenna_pro_tx_usrp

def build_database(flagfile, devicefile):
    """Create sqlite database based on flags file and devices file. Database file name will be based on
    conference name extracted from first line of flags file."""
    flag_input = read_flags(flagfile)
    # Skip first line of flag_input where conference information is stored
    # Add remaining lines to flag_line array
    flag_line = np.asarray(flag_input[1:])

    devices = read_devices(devicefile)

    # Read name of conference from first line of flag file
    conference = flag_input[0][0]
    # Create sqlite database for conference and connect to the database
    conn = sqlite3.connect(conference + ".db")
    c = conn.cursor()
    # Create database schema
    c.execute('''CREATE TABLE flags(chal_id integer primary key,chal_name,flag,module,modopt1,modopt2,
    minwait integer,maxwait integer,freq1,freq2,freq3)''')
    c.execute("CREATE TABLE flag_status(chal_id integer primary key,enabled,lastrun integer,ready)")
    c.execute("CREATE TABLE devices(dev_id integer primary key,dev_string,dev_busy)")
    # Insert flags from flag_line array into database
    c.executemany("INSERT INTO flags VALUES (?,?,?,?,?,?,?,?,?,?,?)", flag_line)
    # Add flag status row for each flag, setting each flag to enabled, lastrun blank, ready
    c.executemany("INSERT INTO flag_status VALUES (?,1,'',1)", flag_line[:, :1])
    # Insert devices from devices array into database, set each device to not busy
    c.executemany("INSERT INTO devices VALUES (?,?,0)", devices)
    conn.commit()
    conn.close()

class transmitter:
    # flag_args:chal_id,flag,modopt1,modopt2,minwait,maxwait,freq1

    def fire_ask(self, device_string, flag_q, device_q, *flag_args):
        print("\nTransmitting ASK\n")
        flag_args = flag_args[0]
        flag = flag_args[1]
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        antenna = get_antenna_port(device_string)
        # print("I ran fire_ask with flag=" + str(flag) + " and freq=" + str(freq))
        ask.main(flag.encode("utf-8").hex(), freq, device_string, antenna)
        sleep(3)
        disable_amp(device_string)
        device_q.put(device_string)
        norandsleep = flag_args[8]
        if(norandsleep == False):
            sleep(randint(mintime, maxtime))
        replaceinqueue = flag_args[7]
        if(replaceinqueue != False):
            flag_q.put(flag_args[0])

    def fire_cw(self, device_string, flag_q, device_q, *flag_args):
        print("\nTransmitting CW\n")
        flag_args = flag_args[0]
        print(device_string)
        flag = flag_args[1]
        speed = int(flag_args[2])
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        antenna = get_antenna_port(device_string)
        # print("I ran fire_cw with flag=" + str(flag) + " and freq=" +
        # str(freq) + " and speed=" + str(speed))
        p = Process(target=cw.main, args=(flag, speed, freq, device_string, antenna))
        p.start()
        p.join()
        sleep(3)
        disable_amp(device_string)
        device_q.put(device_string)
        norandsleep = flag_args[8]
        if(norandsleep == False):
            sleep(randint(mintime, maxtime))
        replaceinqueue = flag_args[7]
        if(replaceinqueue != False):
            flag_q.put(flag_args[0])
        if(p.exitcode != 0):
            sys.exit(p.exitcode)

    def fire_usb(self, device_string, flag_q, device_q, *flag_args):
        print("\nTransmitting USB\n")
        flag_args = flag_args[0]
        wav_src = str(flag_args[1])
        if not os.path.isfile(wav_src):
            print("Unable to find wav file {}".format(wav_src))
            exit(1)
        wav_rate = int(flag_args[2])
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        antenna = get_antenna_port(device_string)
        # print("I ran fire_usb with flag=" + str(wav_src) + " and freq=" +
        # str(freq) + " and wav_rate=" + str(wav_rate))
        usb_tx.main(wav_src, wav_rate, freq, device_string, antenna)
        sleep(3)
        disable_amp(device_string)
        device_q.put(device_string)
        norandsleep = flag_args[8]
        if(norandsleep == False):
            sleep(randint(mintime, maxtime))
        replaceinqueue = flag_args[7]
        if(replaceinqueue != False):
            flag_q.put(flag_args[0])

    def fire_nbfm(self, device_string, flag_q, device_q, *flag_args):
        print("\nTransmitting NBFM\n")
        flag_args = flag_args[0]
        wav_src = str(flag_args[1])
        if not os.path.isfile(wav_src):
            print("Unable to find wav file {}".format(wav_src))
            exit(1)
        wav_rate = int(flag_args[2])
        freq = int(flag_args[6]) * 1000
        mintime = flag_args[4]
        maxtime = flag_args[5]
        antenna = get_antenna_port(device_string)
        # print("I ran fire_nbfm with flag=" + str(wav_src) + " and freq=" +
        # str(freq) + " and wav_rate=" + str(wav_rate))
        nbfm.main(wav_src, wav_rate, freq, device_string, antenna)
        sleep(3)
        disable_amp(device_string)
        device_q.put(device_string)
        norandsleep = flag_args[8]
        if(norandsleep == False):
            sleep(randint(mintime, maxtime))
        replaceinqueue = flag_args[7]
        if(replaceinqueue != False):
            flag_q.put(flag_args[0])

    def fire_pocsag(self, device_string, flag_q, device_q, *flag_args):
        print("\nTransmitting POCSAG\n")
        flag_args = flag_args[0]
        # Parse options from flag_args
        flag = flag_args[1]
        modopt1 = flag_args[2]
        mintime = flag_args[4]
        maxtime = flag_args[5]
        freq = int(flag_args[6]) * 1000
        # Configure options specific to pocsagtx_osmocom script
        pocsagopts = pocsagtx_osmocom.argument_parser().parse_args('')
        pocsagopts.deviceargs = device_string
        pocsagopts.samp_rate = 2400000
        pocsagopts.pagerfreq = freq
        pocsagopts.capcode = int(modopt1)
        pocsagopts.message = flag
        antenna = get_antenna_port(device_string)
        pocsagopts.antenna = antenna
        # Call main in pocsagtx_osmocom, passing in pocsagopts options array
        pocsagtx_osmocom.main(options=pocsagopts)
        # pocsag_tx.main(flag, int(modopt1), freq, device)
        print("Finished TX POCSAG, sleeping for 3sec before returning device")
        sleep(3)
        disable_amp(device_string)
        # print("Slept for 30 seconds")
        device_q.put(device_string)
        # print("Returned Device top pool")
        norandsleep = flag_args[8]
        if(norandsleep == False):
            sleep(randint(mintime, maxtime))
        # sleep(10)
        # print("Slept for 10 seconds")
        replaceinqueue = flag_args[7]
        if(replaceinqueue != False):
            flag_q.put(flag_args[0])
        # print("Returned flag to pool")

    def fire_lrs(self, device_string, flag_q, device_q, *flag_args):
        print("\nTransmitting LRS\n")
        flag_args = flag_args[0]
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
        lrsopts.deviceargs = device_string
        lrsopts.freq = freq
        lrsopts.binfile = outfile
        antenna = get_antenna_port(device_string)
        lrsopts.antenna = antenna
        # Gains below are defaults, added in case they need to be changed
        # lrsopts.bbgain = 20.0
        # lrsopts.ifgain = 20.0
        # lrsopts.rfgain = 47.0

        # Call main in pocsagtx_osmocom, passing in lrsopts options array
        lrs_tx.main(options=lrsopts)
        sleep(3)
        disable_amp(device_string)
        # Delete pager bin file from /tmp/
        os.remove(outfile)
        print("Removed outfile")
        device_q.put(device_string)
        print("Released Radio to pool")
        norandsleep = flag_args[8]
        if(norandsleep == False):
            sleep(randint(mintime, maxtime))
        # sleep(10)
        print("Slept, returning flag to pool")
        replaceinqueue = flag_args[7]
        if(replaceinqueue != False):
            flag_q.put(flag_args[0])
        print("Returned flag to pool")

    def fire_gotenna_pro(self, device_string, flag_q, device_q, *flag_args):
        print("\nTransmitting goTenna Pro\n")
        flag_args = flag_args[0]
        flag = flag_args[1]
        modopts = flag_args[2]
        mintime = flag_args[4]
        maxtime = flag_args[5]
        freq = int(flag_args[6]) * 1000
        norandsleep = flag_args[8]

        devargs = [arg.strip() for arg in device_string.split(",") if arg.strip() != ""]
        devtypes = [arg.lower() for arg in devargs]
        gotenna_module = None
        if("uhd" in devtypes):
            gotenna_module = gotenna_pro_tx_usrp
            gotennaopts = gotenna_module.argument_parser().parse_args(modopts.split())
            gotennaopts.device_addr = ",".join([arg for arg in devargs if arg.lower() != "uhd"])
        elif(any(devtype.startswith("hackrf") for devtype in devtypes)):
            print("goTenna Pro is not supported on HackRF, skipping device {}".format(device_string))
        elif(any(devtype.startswith("bladerf") for devtype in devtypes)):
            gotenna_module = gotenna_pro_tx_bladerf
            gotennaopts = gotenna_module.argument_parser().parse_args(modopts.split())
            gotennaopts.device_args = device_string
            antenna = get_antenna_port(device_string)
            if(antenna != ""):
                gotennaopts.antenna = antenna
        else:
            print("goTenna Pro is not supported on device {}, skipping".format(device_string))

        if(gotenna_module != None):
            gotennaopts.message = flag
            gotennaopts.frequency = freq

            gotenna_module.main(options=gotennaopts)
            sleep(3)
        disable_amp(device_string)
        device_q.put(device_string)

        if(norandsleep == False):
            sleep(randint(mintime, maxtime))
        replaceinqueue = flag_args[7]
        if(replaceinqueue != False):
            flag_q.put(flag_args[0])

class AvoidFreq():
    """Defines a frequency range to avoid."""

    def __init__(self, name, lower_freq, upper_freq):
        self.name = name
        if(lower_freq == upper_freq):
            # Error, frequencies must be different
            print("Error: lower and upper frequencies for avoid freq must be different")

        if(lower_freq > upper_freq):
            # Reverse the lower and upper freqs if they were entered in reverse order
            self.lower_avoid_freq = upper_freq
            self.upper_avoid_freq = lower_freq
        else:
            self.lower_avoid_freq = lower_freq
            self.upper_avoid_freq = upper_freq

    def __str__(self):
        return "Name: {}, {}-{}, Center: {}, Bandwidth: {}".format(self.name, self.lower_avoid_freq, self.upper_avoid_freq, self.get_center_freq(), self.get_bandwidth())

    def is_freq_range_ok(self, lower_freq, upper_freq):
        """Checks if a frequency range avoids the lower and upper bounds of this AvoidFreq object."""

        # Check if either the lower or upper frequencies of the range are within the AvoidFreq range.
        is_lower_freq_in_range = self.lower_avoid_freq <= lower_freq <= self.upper_avoid_freq
        is_upper_freq_in_range = self.lower_avoid_freq <= upper_freq <= self.upper_avoid_freq

        # Check if the lower and upper frequencies are both below or above the AvoidFreq range.
        is_below_range = lower_freq < self.lower_avoid_freq and upper_freq < self.lower_avoid_freq
        is_above_range = lower_freq > self.upper_avoid_freq and upper_freq > self.upper_avoid_freq

        # Check if the requested range fully encompasses the AvoidFreq range
        covers_entire_range = lower_freq <= self.lower_avoid_freq and upper_freq >= self.upper_avoid_freq

        # If either frequency is in the avoid range, return False
        if(is_lower_freq_in_range == True or is_upper_freq_in_range == True):
            return False
        elif(covers_entire_range == True):
            # Return false if the requested range covers the entire AvoidFreq range.
            return False
        elif(is_below_range == True or is_above_range == True):
            # Return True if the requested range is entirely below or above the AvoidFreq range
            return True
        else:
            # Default return False to block the requested frequency range.
            print("WARNING: Default AvoidFreq Block: {}-{}".format(lower_freq, upper_freq))
            return False

    def is_channel_ok(self, center_freq, bandwidth):
        channel_range = AvoidFreq.channel_to_range(center_freq, bandwidth)
        lower_freq = channel_range[0]
        upper_freq = channel_range[1]
        return self.is_freq_range_ok(lower_freq, upper_freq)

    def get_center_freq(self):
        """Returns the center frequency of an AvoidFreq object."""
        return ((self.lower_avoid_freq + self.upper_avoid_freq) / 2)

    def get_bandwidth(self):
        """Returns the bandwidth of an AvoidFreq object."""
        return (self.upper_avoid_freq - self.lower_avoid_freq)

    def channel_to_range(center_freq, bandwidth):
        """Converts a channel with a center frequency and bandwidth to a tuple representing the frequency range."""
        lower_freq = center_freq - math.ceil(bandwidth / 2)
        upper_freq = center_freq + math.ceil(bandwidth / 2)
        return (lower_freq, upper_freq)

    def read_avoid_freqs(avoid_freqs_file):
        """Read file with frequencies to avoid, specified either with channels with a center frequency and bandwidth, or a start and stop frequency range."""
        avoid_freqs = []
        # Read and parse the avoid frequencies file
        with open(avoid_freqs_file) as a:
            avoid_freq_list = []
            raw_avoid_freqs = a.readlines()
            for line in raw_avoid_freqs:
                avoid_freq_list.append(json.loads(line))

        # Create an AvoidFreq object for each item in the file.
        for avoidfreqitem in avoid_freq_list:
            name = avoidfreqitem['name']
            avoidtype = avoidfreqitem['type']
            # Channels are defined by a center frequency and a bandwidth
            if(avoidtype == "channel"):
                avoidcenterfreq = avoidfreqitem['center']
                avoidbandwidth = avoidfreqitem['bandwidth']
                avoidRange = AvoidFreq.channel_to_range(avoidcenterfreq, avoidbandwidth)
                avoidlowerfreq = avoidRange[0]
                avoidupperfreq = avoidRange[1]
                avoidItem = AvoidFreq(name, avoidlowerfreq, avoidupperfreq)
                avoid_freqs.append(avoidItem)
            # Ranges are defined by a lower frequency and an upper frequency.
            elif(avoidtype == "range"):
                avoidlowerfreq = avoidfreqitem['lower_freq']
                avoidupperfreq = avoidfreqitem['upper_freq']
                avoidItem = AvoidFreq(name, avoidlowerfreq, avoidupperfreq)
                avoid_freqs.append(avoidItem)
            else:
                print("Invalid Avoid Type: {}".format(avoidtype))

        return avoid_freqs

    def check_channel_avoid_freqs(avoidFreqs, center_freq, bandwidth):
        """Checks a channel against a list of AvoidFreq objects. Returns True if the channel does not conflict with the AvoidFreq ranges."""
        isFreqOk = True
        for avoid in avoidFreqs:
            isFreqOk = avoid.is_channel_ok(center_freq, bandwidth)
            if(isFreqOk != True):
                print("txfreq: {}, bandwidth: {}, AvoidFreq: {}, isok: {}".format(center_freq, bandwidth, avoid.name, isFreqOk))
                return False
        return isFreqOk

def select_freq(band):
    """Read from frequencies text file, select row that starts with band argument.
    Returns tuple with randomly selected frequency, the minimum frequency for that band, and
    the maximum frequency for that band."""
    with open("frequencies.txt") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == band:
                freq = randint(int(row[1]), int(row[2]))
                return((freq, row[1], row[2]))

def get_challenge_bandwidth(challengetype):
    """Returns the bandwidth for a given challenge type."""
    if(challengetype == "cw"):
        return 100
    elif(challengetype == "nbfm"):
        return 10000
    elif(challengetype == "usb"):
        return 2700
    elif(challengetype == "pocsag"):
        return 9000
    elif(challengetype == "lrs"):
        return 12500
    else:
        print("WARNING: Default case reached in get_challenge_bandwidth.")
        return 10000

def select_dvbt(channel):
    with open("dvbt_channels.txt") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == channel:
                return(int(row[1]))

def read_flags(flags_file):
    """Read lines from flags_file and return a list of lists for each row in the flags_file. 
    The first item in the list contains conference information, and the remaining items in the
    list contain information about each flag."""

    flag_input = []
    with open(flags_file) as f:
        reader = csv.reader(f)
        for row in reader:
            # Skip blank lines in flags file
            if(len(row) != 0):
                flag_input.append(row)
    return flag_input

def read_devices(devices_file):
    """Read lines from devices file, and return a list of lists for each row in the devices file."""
    devices_input = []
    with open(devices_file) as f:
        reader = csv.reader(f, quotechar='"')
        for row in reader:
            devices_input.append(row)
    return devices_input

# Parse bladerf serial number from device string
def parse_bladerf_ser(device):
    bladerfdevind = device.find("bladerf=")
    serialstart = bladerfdevind + 8
    serialend = serialstart + 32
    bladeserial = device[serialstart:serialend]
    return bladeserial

def disable_amp(device_string):
    """Turn off biastee if the device is a bladerf with the biastee enabled"""
    if(device_string.find("bladerf") != -1 and device_string.find("biastee=1") != -1):
        bladeserial = parse_bladerf_ser(device_string)
        serialarg = '*:serial={}'.format(bladeserial)
        subprocess.run(['bladeRF-cli', '-d', serialarg, 'set', 'biastee', 'tx', 'off'])
    else:
        # If different logic is required for other device types, it should go here.
        pass

def get_antenna_port(device):
    """Given a device string, return the string to pass in to the antenna parameter. Default return value is an empty string."""
    # empty string is default value for antenna argument
    antenna = ""
    # bladerf with serial 1c4842b8d80e43438c042dbd752c6640 has a broken TX1 port
    if(device.find("bladerf=1c4842b8d80e43438c042dbd752c6640") != -1):
        antenna = "TX2"
        print("Set antenna to TX2")
    else:
        # If you would like to use a different TX port, other than the default for your SDR, the logic to do so should go here.
        antenna = ""
        #print("Antenna set to default empty string. device: {}".format(device))
    return antenna

def argument_parser():
    parser = argparse.ArgumentParser(description="A script to run SDR challenges on multiple SDR devices.")
    parser.add_argument("-f", '--flagfile', help="Flags file")
    parser.add_argument("-d", '--devicefile', help="Devices file")
    parser.add_argument("-a", '--avoidfreqsfile', help="Avoid Frequencies file")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-t", "--test", help="Run each challenge once to test flags.", action="store_true")
    return parser

def main(options=None):
    if options is None:
        options = argument_parser().parse_args()

    t = transmitter()
    args = options
    flagfile = args.flagfile
    devicefile = args.devicefile
    avoidfreqsfile = args.avoidfreqsfile
    verbose = args.verbose
    test = args.test

    # Read and parse the Avoid Frequencies file
    avoidFreqs = []
    if(avoidfreqsfile is not None):
        avoidFreqs = AvoidFreq.read_avoid_freqs(avoidfreqsfile)

    global conference
    # Create thread safe FIFO queues for devices and flags
    device_Q = Queue()
    flag_Q = Queue()
    # Read flags file
    flag_input = read_flags(flagfile)
    # Extract conference name from first item returned by read_flags
    conference = flag_input[0][0]
    # Check to see if database for conference name exists, create it if not
    if not os.path.exists(conference + ".db"):
        build_database(flagfile, devicefile)

    # Connect to conference database
    conn = sqlite3.connect(conference + ".db")
    c = conn.cursor()

    # Create a list of device IDs from devices in the database
    c.execute("SELECT dev_id,dev_string FROM devices")
    dev_list = c.fetchall()
    for row in dev_list:
        device_Q.put(row[1])

    # Create a list of challenge IDs based on flags that are enabled in the database
    c.execute("SELECT chal_id FROM flag_status WHERE enabled=1")
    flag_list = c.fetchall()
    flag_list = list(sum(flag_list, ()))
    # Randomize order of flag_list except when testing flags
    if(test != True):
        shuffle(flag_list)
    print(flag_list)
    flag_count = len(flag_list)
    challenges_transmitted = 0
    # Put flag_list into thread safe flag_Q
    for row in flag_list:
        flag_Q.put(row)

    dev_available = device_Q.get()

    jobs = []

    try:
        while dev_available != None:
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

            # Convert transmit frequency from kHz to Hz
            txfreq_hz = txfreq * 1000
            # Default spectrum paint bandwidth is 2 MHz
            spectrum_paint_bandwidth = 2000000

            isFreqOk = AvoidFreq.check_channel_avoid_freqs(avoidFreqs, txfreq_hz, spectrum_paint_bandwidth)
            # Only spectrum paint if the spectrum paint avoids all AvoidFreq ranges
            if(isFreqOk == True):
                # Paint waterfall every time during the CTF, or only once when testing
                if(test != True or challenges_transmitted == 0):
                    print(f"\nPainting Waterfall on {txfreq}\n")
                    # spectrum_paint.main(current_chal[7] * 1000, fetch_device(dev_available))
                    antenna = get_antenna_port(dev_available)

                    p = Process(target=spectrum_paint.main, args=(txfreq * 1000, dev_available, antenna))  # , daemon=True)
                    p.start()
                    p.join()
                    disable_amp(dev_available)
            else:
                print("WARNING: Skipped spectrum paint due to Avoid Frequency conflict.")

            challenge_bandwidth = get_challenge_bandwidth(cc_module)
            challenge_channel_center = txfreq_hz
            if(cc_module == "usb"):
                # For the USB flowgraph, the tx freq is not the center of the channel.
                # Calculate where the center of the transmission will be, and use that to check the AvoidFreq ranges.
                challenge_channel_center = txfreq_hz + int(challenge_bandwidth / 2)
            else:
                challenge_channel_center = txfreq_hz
            isChallengeFreqOk = AvoidFreq.check_channel_avoid_freqs(avoidFreqs, challenge_channel_center, challenge_bandwidth)

            if(isChallengeFreqOk == True):
                print(f"\nStarting {cc_name} on {txfreq}")
                # Create list of challenge module arguments, using txfreq to allow setting random freq here instead of in the challenge module
                replaceinqueue = True
                norandsleep = False
                if(test):
                    replaceinqueue = False
                    norandsleep = True
                challengeargs = [cc_id, cc_flag, cc_modopt1, cc_modopt2, cc_minwait, cc_maxwait, txfreq, replaceinqueue, norandsleep]
                p = Process(target=getattr(t, "fire_" + cc_module), args=(dev_available, flag_Q, device_Q, challengeargs))
                p.start()
                if(test == True):
                    jobs.append(p)
                challenges_transmitted += 1
            else:
                print("WARNING: Challenge skipped due to Avoid Frequency conflict.")
            # #we need a way to know if p.start errored or not
            # os.system("echo " + freq_or_range + " > /run/shm/wctf_status/" + current_chal[8] + "_sdr")
            # os.system('''timeout 15 ssh -F /root/wctf/liludallasmultipass/ssh/config -oStrictHostKeyChecking=no -oConnectTimeout=10 -oPasswordAuthentication=no -n scoreboard echo ''' + freq_or_range + " > /run/shm/wctf_status/" + current_chal[8] + "_sdr")
            dev_available = device_Q.get()
            sleep(1)
            if(test == True and flag_Q.empty()):
                returnvalue = 0
                print("Testing complete")
                while(len(jobs)>0):
                    proc = jobs[0]
                    exitcode = proc.exitcode
                    jobs.remove(proc)
                    if(exitcode == None):
                        jobs.append(proc)
                        continue
                    if(exitcode != 0):
                        print("Failed")
                        returnvalue = 1
                        exit(returnvalue)
                    #print("exitcode: {}".format(proc.exitcode))
                    proc.join()
                exit(returnvalue)
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
