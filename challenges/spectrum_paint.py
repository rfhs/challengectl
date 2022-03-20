#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Spectrum Paint
# GNU Radio version: 3.7.13.5
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import signal
import osmosdr
import paint
import pmt
import time


class spectrum_paint(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Spectrum Paint")

        ##################################################
        # Variables
        ##################################################
        global frequency
        global device
        self.samp_rate = samp_rate = 2000000
        self.frequency = frequency  # = 148e6
        self.dev = dev  # = "blade=0"

        ##################################################
        # Blocks
        ##################################################
        self.paint_paint_bc_0 = paint.paint_bc(113, 25, paint.EQUALIZATION_OFF, paint.INTERNAL, 1)
        self.osmosdr_sink_0 = osmosdr.sink(args="numchan=" + str(1) + " " + dev)
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(frequency, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(50, 0)
        self.osmosdr_sink_0.set_if_gain(20, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(4096, 4096 + 4096 / 8, 0, '')
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex * 1, 4096)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char * 1, 'challenges/rfhs.bin', False)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.paint_paint_bc_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.paint_paint_bc_0, 0), (self.blocks_stream_to_vector_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.osmosdr_sink_0.set_center_freq(self.frequency, 0)

    def get_dev(self):
        return self.dev

    def set_dev(self, dev):
        self.dev = dev


# def sigterm_handler(signal, frame):
#     print('Killed')
#     main.tb.stop()


def main(freq, device, top_block_cls=spectrum_paint, options=None):

    global frequency
    global dev
    frequency = freq
    dev = str(device)

    tb = top_block_cls()
    tb.start()
    tb.wait()


# signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    main()
