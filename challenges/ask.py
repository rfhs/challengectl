#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Russ Test
# Generated: Wed Jan  4 20:01:00 2017
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import time
import numpy as np

center_freq=0
dev="0a"
ask=()
ask_code='0,'

class russ_test(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Russ Test")

        ##################################################
        # Variables
        ##################################################
        self.interp = interp = 600
        self.baud_rate = baud_rate = 3211
        self.samp_rate_0 = samp_rate_0 = baud_rate*interp
        self.samp_rate = samp_rate = baud_rate*interp
        self.center_freq = center_freq
        self.dev = dev

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + str(dev) )
        self.osmosdr_sink_0.set_time_source("mimo", 0)
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(center_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(33, 0)
        self.osmosdr_sink_0.set_if_gain(32, 0)
        self.osmosdr_sink_0.set_bb_gain(32, 0)
        self.osmosdr_sink_0.set_antenna("", 0)
        self.osmosdr_sink_0.set_bandwidth(2000000, 0)

        self.blocks_vector_source_x_0 = blocks.vector_source_c(ask + [0]*5321, False, 1, [])
	#self.blocks_vector_source_x_0 = blocks.vector_source_c([1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]*10 + [0]*5321, False, 1, [])
	#self.blocks_vector_source_x_0 = blocks.vector_source_c([ask]*10 + [0]*53321, False, 1, [])
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex*1, interp)
        self.blocks_moving_average_xx_0 = blocks.moving_average_cc(20, 0.9/20, 4000)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_moving_average_xx_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_repeat_0, 0))

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp
        self.set_samp_rate(self.baud_rate*self.interp)
        self.set_samp_rate_0(self.baud_rate*self.interp)

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.set_samp_rate(self.baud_rate*self.interp)
        self.set_samp_rate_0(self.baud_rate*self.interp)

    def get_samp_rate_0(self):
        return self.samp_rate_0

    def set_samp_rate_0(self, samp_rate_0):
        self.samp_rate_0 = samp_rate_0

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.osmosdr_sink_0.set_center_freq(self.center_freq, 0)

    def get_ask(self):
        return self.ask

    def set_ask(self, ask):
        self.ask = ask
        self.blocks_vector_source_x_0.set_data(self.ask, [])


def main(msg, freq, device, top_block_cls=russ_test, options=None):

    global center_freq
    global dev
    global ask

    # parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    # parser.add_option("-m", "--msg", dest="msg",
    #               help="Your text message.", metavar="MSG")
    # parser.add_option("-f", "--freq", dest="frequency", type="int",
    #               help="Frequency to transmit.", metavar="FREQ")
    # parser.add_option("-d", "--dev", dest="dev",
    #               help="Dev to transmit on.", metavar="DEV")
    #
    # (options, args) = parser.parse_args()
    #
    # mandatories = ['msg', 'frequency', 'dev']
    # for m in mandatories:
    #   if options.__dict__[m] is None:
    #     print "You forgot an arguement"
    #     parser.print_help()
    #     exit(-1)
    dev = device
    #msg = ""

    ask_code='0,'
    #for char in options.msg:
        #ask_code=ask_code+int(char)

    scale = 16
    num_of_bits = 8
    str1=bin(int(msg, scale))[2:].zfill(num_of_bits)
    tmp = ','.join(list(str1))
    ask_code=ask_code+tmp+',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'


    ask_split=ask_code.split(',')

    #ask=([1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])*10


    ask=map(int,ask_split)*10

    center_freq = freq

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
