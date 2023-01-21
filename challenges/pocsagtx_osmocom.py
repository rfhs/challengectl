#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Pocsagtx Osmocom
# Author: cstone@pobox.com
# Description: Example flowgraph for POCSAG transmitter
# GNU Radio version: 3.8.5.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.filter import pfb
import math
# import mixalot
import osmosdr
import time


class pocsagtx_osmocom(gr.top_block):

    def __init__(self, capcode=1234567, deviceargs="hackrf=0", message="DEF CON 30 HOM3C0MING", pagerfreq=433500000, samp_rate=2400000):
        gr.top_block.__init__(self, "Pocsagtx Osmocom")

        ##################################################
        # Parameters
        ##################################################
        self.capcode = capcode
        self.deviceargs = deviceargs
        self.message = message
        self.pagerfreq = pagerfreq
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.symrate = symrate = 38400
        self.max_deviation = max_deviation = 4500.0

        ##################################################
        # Blocks
        ##################################################
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
            float(samp_rate)/float(symrate),
            taps=None,
            flt_size=32)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + deviceargs
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(pagerfreq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(10, 0)
        self.osmosdr_sink_0.set_if_gain(20, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.mixalot_pocencode_0 = mixalot.pocencode(1, 512, capcode, message, symrate)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(0.7)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.analog_frequency_modulator_fc_0 = analog.frequency_modulator_fc(2.0 * math.pi * max_deviation / float(symrate))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_frequency_modulator_fc_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.analog_frequency_modulator_fc_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.mixalot_pocencode_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))


    def get_capcode(self):
        return self.capcode

    def set_capcode(self, capcode):
        self.capcode = capcode

    def get_deviceargs(self):
        return self.deviceargs

    def set_deviceargs(self, deviceargs):
        self.deviceargs = deviceargs

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message

    def get_pagerfreq(self):
        return self.pagerfreq

    def set_pagerfreq(self, pagerfreq):
        self.pagerfreq = pagerfreq
        self.osmosdr_sink_0.set_center_freq(self.pagerfreq, 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        self.pfb_arb_resampler_xxx_0.set_rate(float(self.samp_rate)/float(self.symrate))

    def get_symrate(self):
        return self.symrate

    def set_symrate(self, symrate):
        self.symrate = symrate
        self.analog_frequency_modulator_fc_0.set_sensitivity(2.0 * math.pi * self.max_deviation / float(self.symrate))
        self.pfb_arb_resampler_xxx_0.set_rate(float(self.samp_rate)/float(self.symrate))

    def get_max_deviation(self):
        return self.max_deviation

    def set_max_deviation(self, max_deviation):
        self.max_deviation = max_deviation
        self.analog_frequency_modulator_fc_0.set_sensitivity(2.0 * math.pi * self.max_deviation / float(self.symrate))




def argument_parser():
    description = 'Example flowgraph for POCSAG transmitter'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "-c", "--capcode", dest="capcode", type=intx, default=1234567,
        help="Set capcode [default=%(default)r]")
    parser.add_argument(
        "-d", "--deviceargs", dest="deviceargs", type=str, default="hackrf=0",
        help="Set deviceargs [default=%(default)r]")
    parser.add_argument(
        "-m", "--message", dest="message", type=str, default="DEF CON 30 HOM3C0MING",
        help="Set message [default=%(default)r]")
    parser.add_argument(
        "-f", "--pagerfreq", dest="pagerfreq", type=eng_float, default="433.5M",
        help="Set pagerfreq [default=%(default)r]")
    parser.add_argument(
        "-s", "--samp-rate", dest="samp_rate", type=eng_float, default="1.0M",
        help="Set samp_rate [default=%(default)r]")
    return parser


def main(top_block_cls=pocsagtx_osmocom, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(capcode=options.capcode, deviceargs=options.deviceargs, message=options.message, pagerfreq=options.pagerfreq, samp_rate=options.samp_rate)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
