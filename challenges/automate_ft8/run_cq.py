#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import threading
import subprocess
import os
import re
from datetime import datetime
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/home/corey/automate_ft8/ft8_qso.conf')

my_call = str(parser.get('main', 'my_call_sign'))
my_grid = str(parser.get('main', 'my_grid_square'))
tx_cycle = str(parser.get('main', 'transmit_cycle'))
rx_cycle = str(parser.get('main', 'receive_cycle'))
flag = str(parser.get('main', 'flag'))
calling_cq = True
retry = 0
their_call = ''
their_grid = ''
snr = ''
their_msg = ''


def tx(e):
    global tx_cycle
    while not e.isSet():
        print("\nStarting TX")
        os.system('python ft8_tx.py ' + tx_cycle)  # 2> /dev/null')
        time.sleep(8)
        print("\nExiting TX")


def rx(e):
    global rx_cycle
    while not e.isSet():
        print("\nStarting RX")
        os.system('python ft8_rx.py ' + rx_cycle)  # 2> /dev/null')
        parse_rx()
        time.sleep(8)
        print("\nExiting RX")


class qso_tracker:
    def __init__(self, current_call, step):
        self.current_call = current_call
        self.step = step
        self.max_step = 3
        self.reply_attempt = 0


def tx_cq(my_call, my_grid):
    os.system('./ft8encode "CQ ' + my_call + ' ' + my_grid + '" 1000 0 0 0 0 1 40')


def tx_report(their_call, my_call, snr):
    if int(snr) >= 0:  # Add + if the number is positive
        os.system('./ft8encode "' + their_call + ' ' + my_call + ' +' + str(snr).zfill(2) + '" 1000 0 0 0 0 1 40')
    else:
        os.system('./ft8encode "' + their_call + ' ' + my_call + ' ' + str(snr).zfill(2) + '" 1000 0 0 0 0 1 40')


def tx_73(their_call, my_call):
    os.system('./ft8encode "' + their_call + ' ' + my_call + ' RR73" 1000 0 0 0 0 1 40')

def tx_flag(flag):
    os.system('./ft8encode "' + flag + '" 1000 0 0 0 0 1 40')

def chk_blacklist(their_call):
    try:
        blacklist = open('./captures/blacklist.txt', "r+")
        check_blacklist = blacklist.readlines()
        blacklist.close()
        for line in check_blacklist:
            if their_call in line:
                return True
            else:
                return False
    except:
        return False


def parse_rx():
    global calling_cq
    global retry
    global rx_my_call
    global their_call
    global their_msg
    global qso
    global flag
    now = datetime.now()
    rx_time = now.strftime("[%m/%d/%Y %H:%M:%S]")
    replies = []
    try:
        ft8_decode = subprocess.check_output('./ft8decode 300 3000 3 ./ft8rx.wav', shell=True)
        print("\nReceived Messages:\n" + ft8_decode)
        if ft8_decode != '':
            qso_list = open('./captures/text_rx.txt', "a+")
            qso_list.write(rx_time + ' ' + ft8_decode)
            qso_list.close()
        ft8_decode_lines = ft8_decode.splitlines()
        # print(ft8_decode_lines)
        for line in range(len(ft8_decode_lines)):
            if not calling_cq:
                if qso.current_call in ft8_decode_lines[line]:
                    collapsedstring = ' '.join(ft8_decode_lines[line].split())
                    # print(collapsedstring)
                    replies.append(collapsedstring.split(' '))
            elif my_call in ft8_decode_lines[line]:
                collapsedstring = ' '.join(ft8_decode_lines[line].split())
                # print(collapsedstring)
                replies.append(collapsedstring.split(' '))
        # print(replies)
        chosen_reply = max(replies, key=lambda x: x[1])

        print(chosen_reply)
        snr = chosen_reply[1]  # The second number is always the SNR
        # In a properly formatted message this will be the receiver's call sign
        rx_my_call = chosen_reply[6]
        # In a properly formatted message this should always be the senders call sign
        their_call = chosen_reply[7]
        # This position will either be a grid square (e.g. FM19), a signal report (e.g. -10 or R-10),
        # "RR73", or "73", which closes the QSO
        their_msg = chosen_reply[8]
        print("\nTheir SNR: " + snr)
        print("They're calling: " + rx_my_call)
        print("They are " + their_call)
        print("They said " + their_msg)
    except:
         print("\nNo Reply")
         chosen_reply = ''
         rx_my_call = ''

    rules = [chosen_reply != '',
             rx_my_call == my_call,
             qso.current_call == their_call or 'NOCALL',
             not chk_blacklist(their_call),
             qso.reply_attempt < 9]
    if all(rules):
        print("\nReply Attempt Number: " + str(qso.reply_attempt + 1))
        if re.search("[A-R]{2}\d{2}", their_msg):  # and qso.step == 1:
            if qso.step == 1:
                tx_report(their_call, my_call, snr)
                calling_cq = False
                retry = 0
                qso.step = 2
                qso.current_call = their_call
                qso.reply_attempt = 0
            else:
                print("\nResponding again...")
                qso.reply_attempt += 1
        elif re.search("[R][+|-]\d{2}", their_msg):  # and qso.step == 2:
            if qso.step == 2:
                tx_73(their_call, my_call)
                calling_cq = False
                retry = 0
                qso.step = 3
                qso.reply_attempt = 0
            else:
                print("\nResending Report...")
                qso.reply_attempt += 1
        elif their_msg == "73" and qso.step == 3:
            tx_flag(flag)
            retry = 2
            qso.step = 4
            calling_cq = False

            blacklist = open('./captures/blacklist.txt', "a+")
            blacklist.write(qso.current_call + "\n")
            blacklist.close()
            # award points
            qso.current_call = 'NOCALL'
            qso.reply_attempt = 0
        elif qso.step == 4:
            tx_cq(my_call, my_grid)
            calling_cq = True
            retry = 0
            qso.step = 1
            blacklist = open('./captures/blacklist.txt', "a+")
            blacklist.write(qso.current_call + "\n")
            blacklist.close()
            # award points
            qso.current_call = 'NOCALL'
            qso.reply_attempt = 0

    else:
        # repeat last action, up to 4 times if not cq
        if not calling_cq and retry < 4:
            retry += 1
            qso.reply_attempt += 1
        elif not calling_cq and retry >= 4:
            tx_cq(my_call, my_grid)
            retry = 0
            calling_cq = True
            qso.reply_attempt = 0
        else:
            print("\nCalling CQ")
            calling_cq = True


def main():
    tx_cq(my_call, my_grid)
    e = threading.Event()
    t = threading.Thread(name='Transmit', target=tx, args=(e,))
    r = threading.Thread(name='Receive', target=rx, args=(e,))
    t.daemon = True
    r.daemon = True
    t.start()
    r.start()

    raw_input("\n\nPress Enter to Exit: ")
    e.set()
    print("\n\nKilling threads, plase wait")
    t.join()
    r.join()
    quit()


qso = qso_tracker('NOCALL', 1)
if __name__ == "__main__":
    main()
