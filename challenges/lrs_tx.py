#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: LRS TX
# GNU Radio version: 3.8.2.0

from gnuradio import analog
from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time


class lrs_tx(gr.top_block):

    def __init__(self, bbgain=20, binfile="pager.bin", deviceargs="hackrf", freq=467750000, ifgain=20, rfgain=47):
        gr.top_block.__init__(self, "LRS TX")

        ##################################################
        # Parameters
        ##################################################
        self.bbgain = bbgain
        self.binfile = binfile
        self.deviceargs = deviceargs
        self.freq = freq
        self.ifgain = ifgain
        self.rfgain = rfgain

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2400000

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + deviceargs
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(rfgain, 0)
        self.osmosdr_sink_0.set_if_gain(ifgain, 0)
        self.osmosdr_sink_0.set_bb_gain(bbgain, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_float*1, 3190)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_float*1, binfile, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.analog_frequency_modulator_fc_0 = analog.frequency_modulator_fc(6.26)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_frequency_modulator_fc_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.analog_frequency_modulator_fc_0, 0))


    def get_bbgain(self):
        return self.bbgain

    def set_bbgain(self, bbgain):
        self.bbgain = bbgain
        self.osmosdr_sink_0.set_bb_gain(self.bbgain, 0)

    def get_binfile(self):
        return self.binfile

    def set_binfile(self, binfile):
        self.binfile = binfile
        self.blocks_file_source_0.open(self.binfile, False)

    def get_deviceargs(self):
        return self.deviceargs

    def set_deviceargs(self, deviceargs):
        self.deviceargs = deviceargs

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)

    def get_ifgain(self):
        return self.ifgain

    def set_ifgain(self, ifgain):
        self.ifgain = ifgain
        self.osmosdr_sink_0.set_if_gain(self.ifgain, 0)

    def get_rfgain(self):
        return self.rfgain

    def set_rfgain(self, rfgain):
        self.rfgain = rfgain
        self.osmosdr_sink_0.set_gain(self.rfgain, 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)




def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "-b", "--bbgain", dest="bbgain", type=eng_float, default="20.0",
        help="Set bbgain [default=%(default)r]")
    parser.add_argument(
        "-r", "--binfile", dest="binfile", type=str, default="pager.bin",
        help="Set binfile [default=%(default)r]")
    parser.add_argument(
        "-d", "--deviceargs", dest="deviceargs", type=str, default="hackrf",
        help="Set deviceargs [default=%(default)r]")
    parser.add_argument(
        "-f", "--freq", dest="freq", type=intx, default=467750000,
        help="Set freq [default=%(default)r]")
    parser.add_argument(
        "-i", "--ifgain", dest="ifgain", type=eng_float, default="20.0",
        help="Set ifgain [default=%(default)r]")
    parser.add_argument(
        "-g", "--rfgain", dest="rfgain", type=eng_float, default="47.0",
        help="Set rfgain [default=%(default)r]")
    return parser


def main(top_block_cls=lrs_tx, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(bbgain=options.bbgain, binfile=options.binfile, deviceargs=options.deviceargs, freq=options.freq, ifgain=options.ifgain, rfgain=options.rfgain)

    # def sig_handler(sig=None, frame=None):
    #     tb.stop()
    #     tb.wait()

    #     sys.exit(0)

    # signal.signal(signal.SIGINT, sig_handler)
    # signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
