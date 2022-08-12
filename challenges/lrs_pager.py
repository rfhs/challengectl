#!/usr/bin/python

"""
Written by: Tony Tiger 6/2019

This program generates manchester encoded data packets for LRS pagers and GNU Radio.

Output file name: pager.bin

Watch the YouTube video for more information: https://www.youtube.com/watch?v=ycLLb4eVZpI

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import re
import struct
import argparse
import random


def encode_manchester( bin_list, verbose ):

      pre = []  # create extra preambles to wake up the pager
      for x in range(0,50): 
            pre.append('1')
            pre.append('0')

      l = re.findall('.', "".join( pre + bin_list  ) )  # join the preamble and the rest of the packet

      m = []
      if(verbose):
          print('\n')
          print("".join(str(x) for x in l))  # convert list to string

      for x in l:   # convert to manchaster coding
           if( x == '0'):
               m.append(1)
               m.append(0)

           if( x == '1'):
               m.append(0)
               m.append(1)
      return m


# calculate the crc
def calculate_crc( pre, sink_word, rest_id, station_id, pager_n, alert_type, printkey, verbose ):

    l = re.findall('..', pre + sink_word + rest_id + station_id +  pager_n + '0000000000' + alert_type  )

    bin_array = []
    for c in l:
         bin_array.append ( (format( int(c, 16) , '08b')))

    sum=0
    for b in bin_array:
         sum +=  int(b , 2)

    if(verbose):
        print('Full Packet: {0} {1} {2} {3} {4} {5} {6} {7}'.format( pre, sink_word, rest_id, station_id, pager_n, '0000000000', alert_type, format( ( sum % 255), '02x' )))

    if(verbose or printkey):
        rfctfkey = '{0}{1}{2}{3}{4}{5}{6}'.format( sink_word, rest_id, station_id, pager_n, '0000000000', alert_type, format( ( sum % 255), '02x' ))
        print('')
        print('RFCTF Key: {0}'.format(rfctfkey))
        print('')
        print('Keystore line:')
        rfctfpoints = 75
        print('LRS_PAGER,{0},{1},stat,LRS Pager RX'.format(rfctfkey, rfctfpoints))

    bin_array.append( format( ( sum % 255), '08b') )
    return bin_array


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outputfile", default="pager.bin", help="Output file")
    parser.add_argument("-s", "--systemid", type=int, default=1, help="Pager System ID, 0-255")
    parser.add_argument("-p", "--pagerid", type=int, default=1, help="Pager ID, 0-1023")
    parser.add_argument("-pf", "--function", type=int, default=1, help="Page function. Flash/Vibe 30 seconds: 1, Flash/Vibe 1 second: 10, Beep 3 times: 4")
    parser.add_argument("-k", "--printkey", action="store_true", help="Print RFCTF Key")
    parser.add_argument("-r", "--random", action="store_true", help="Select random values for systemid, pagerid, and function, then print RFCTF key.")
    parser.add_argument("-v", "--verbose", action="store_true")
    #1 Flash 30 Seconds, 2 Flash 5 Minutes
    #3 Flash/Beep 5X5
    #4 Beep 3 Times
    #5 Beep 5 Minutes
    #6 Glow 5 Minutes
    #7 Glow/Vib 15 Times
    #10 Flash/Vib 1 Second
    #68 beep 3 times
    return parser


def main(options=None):
    if options is None:
        options = argument_parser().parse_args()

    ##########################################
    # main program start                     #
    ##########################################
    
    args = options
    if(args.verbose):
        print("System ID: 0x{:02x}".format(args.systemid))
        print("Pager ID: 0x{:02x}".format(args.pagerid))
        print("Page Function: 0x{:02x}".format(args.function))
        print("Output file: {}".format(args.outputfile))

    randomkey = args.random

    if(randomkey):
        rest_id = random.randint(0,255)
    elif(args.systemid):
        rest_id = args.systemid
    else:
        try:
            rest_id=int(input('\nEnter restaurant id 0-255: '))
        except ValueError:
            print("Not a number")

    if(randomkey):
        pagers = str(random.randint(0,1023))
    elif(args.pagerid):
        pagers = str(args.pagerid)
    else:
        try:
            pagers=(input('Enter one or more pager numbers 0-1023 : '))
        except ValueError:
            print("Not a number")

    pager_list = []
    pager_list = list(map( int, re.split('\s+',pagers)))

    if(randomkey):
        alert_type = random.choice([1, 10, 4])
    elif(args.function):
        alert_type = args.function
    else:
        print('1 Flash 30 Seconds\n2 Flash 5 Minutes\n3 Flash/Beep 5X5\n4 Beep 3 Times\n5 Beep 5 Minutes\n6 Glow 5 Minutes\n7 Glow/Vib 15 Times\n10 Flash/Vib 1 Second\n68 beep 3 times\n')

        try:
            alert_type=int(input('Enter alert type: '))
        except ValueError:
            print("Not a number")

    outputfile = args.outputfile
    if(random):
        printkey = True
    else:
        printkey = args.printkey
    verbose = args.verbose

    if(printkey):
        print('SDR Simple Challenge Runner line:')
        print('16,LRS_PAGER,-s {0} -p {1} -pf {2},lrs,,0'.format(rest_id, pagers, alert_type))

    handle = open(outputfile, 'wb')

    data = []
    for pager_n in pager_list:
        crc_out = ( calculate_crc( format(11184810, '06x') , format( 64557,'04x'), format(rest_id, '02x'), '0', format( pager_n  ,'03x' ), format(alert_type, '02x'), printkey, verbose ) )

        data = encode_manchester( crc_out, verbose )
        [ data.append(0) for x in range(0,100) ]

        if(verbose):
            print('\n');
            print("".join(str(x) for x in data))
            print('\n')

        for d in data:
            if d == 0:
                handle.write(struct.pack('f', .0001)) 
            elif d == 1:
                handle.write(struct.pack('f', 1)) 
            else:
                print("Error detected in data")
                sys.exit()

    handle.close()


if __name__ == '__main__':
    main()
