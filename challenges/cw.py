#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Cw
# Generated: Thu Jan  5 21:05:30 2017
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import time
import signal
import numpy as np

CODE = {
    'A': '1,0,1,1,1,0',
    'B': '1,1,1,0,1,0,1,0,1,0',
    'C': '1,1,1,0,1,0,1,1,1,0,1,0',
    'D': '1,1,1,0,1,0,1,0',
    'E': '1,0',
    'F': '1,0,1,0,1,1,1,0,1,0',
    'G': '1,1,1,0,1,1,1,0,1,0',
    'H': '1,0,1,0,1,0,1,0',
    'I': '1,0,1,0',
    'J': '1,0,1,1,1,0,1,1,1,0,1,1,1,0',
    'K': '1,1,1,0,1,0,1,1,1,0',
    'L': '1,0,1,1,1,0,1,0,1,0',
    'M': '1,1,1,0,1,1,1,0',
    'N': '1,1,1,0,1,0',
    'O': '1,1,1,0,1,1,1,0,1,1,1,0',
    'P': '1,0,1,1,1,0,1,1,1,0,1,0',
    'Q': '1,1,1,0,1,1,1,0,1,0,1,1,1,0',
    'R': '1,0,1,1,1,0,1,0',
    'S': '1,0,1,0,1,0',
    'T': '1,1,1,0',
    'U': '1,0,1,0,1,1,1,0',
    'V': '1,0,1,0,1,0,1,1,1,0',
    'W': '1,0,1,1,1,0,1,1,1,0',
    'X': '1,1,1,0,1,0,1,0,1,1,1,0',
    'Y': '1,1,1,0,1,0,1,1,1,0,1,1,1,0',
    'Z': '1,1,1,0,1,1,1,0,1,0,1,0',
    '0': '1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0',
    '1': '1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0',
    '2': '1,0,1,0,1,1,1,0,1,1,1,0,1,1,1,0',
    '3': '1,0,1,0,1,0,1,1,1,0,1,1,1,0',
    '4': '1,0,1,0,1,0,1,0,1,1,1,0',
    '5': '1,0,1,0,1,0,1,0,1,0',
    '6': '1,1,1,0,1,0,1,0,1,0,1,0',
    '7': '1,1,1,0,1,1,1,0,1,0,1,0,1,0',
    '8': '1,1,1,0,1,1,1,0,1,1,1,0,1,0,1,0',
    '9': '1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,0',
    '.': '1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0',
    ',': '1,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,1,1,0',
    '?': '1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,0',
    '!': '1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0',
    ' ': '0,0,0',
    '-': '1,1,1,0,1,0,1,0,1,0,1,0,1,1,1,0',
    ':': '1,1,1,0,1,1,1,0,1,1,1,0,1,0,1,0,1,0',
    '_': '1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0'
}

morse_code = '0,'
morse = ()
wpm = 1
freq = 0
dev = "0a"


class cw(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Cw")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 48000
        #self.morse = morse = (1,0,1,0,1,0,1,1,1,1,1,1,1,1)
        self.morse = morse
        self.dev = dev

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=2000000,
            decimation=samp_rate,
            taps=[],
            fractional_bw=0.0,
        )
        #self.osmosdr_sink_0 = osmosdr.sink(args="numchan=" + str(1) + " " + str(dev))
        self.osmosdr_sink_0 = osmosdr.sink(args=str(dev))
        self.osmosdr_sink_0.set_sample_rate(2000000)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(37, 0)
        self.osmosdr_sink_0.set_if_gain(32, 0)
        self.osmosdr_sink_0.set_bb_gain(32, 0)
        self.osmosdr_sink_0.set_antenna(ant, 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self.blocks_vector_source_x_0 = blocks.vector_source_c(morse, False, 1, [])
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex * 1, wpm * 100)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 700, 1, 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))

    def get_wpm(self):
        return self.wpm

    def set_wpm(self, wpm):
        self.wpm = wpm

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_morse(self):
        return self.morse

    def set_morse(self, morse):
        self.morse = morse
        self.blocks_vector_source_x_0.set_data(self.morse, [])

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_freq(self.freq, 0)


# def sigterm_handler(signal, frame):
#     print('Killed')
#     main.tb.stop()


def main(mesg, wordspm, frequency, device, antenna, top_block_cls=cw, options=None):
    global morse
    global wpm
    global freq
    global dev
    global ant

    wpm = wordspm
    freq = frequency
    dev = device
    ant = antenna

    morse_code = '0,'
    for char in mesg:
        morse_code = morse_code + CODE[char.upper()] + ',0,'

    morse_code = morse_code + '0,0,0,0,0,0,0,0,0,0,0'

    m_split = morse_code.split(',')
    #morse=np.asarray(map(int,m_split))

    morse = list(map(int, m_split))

    main.tb = top_block_cls()
    main.tb.start()
    main.tb.wait()


# signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-m", "--msg", dest="msg",
                      help="Your text message.", metavar="MSG")
    parser.add_option("-s", "--speed", dest="wpm", type="int",
                      help="Speed: lower is faster.", metavar="WPM")
    parser.add_option("-f", "--freq", dest="frequency", type="int",
                      help="Frequency to transmit.", metavar="FREQ")
    parser.add_option("-d", "--dev", dest="dev",
                      help="Dev to transmit on.", metavar="DEV")
    parser.add_option("-a", "--ant", dest="ant",
                      help="Antenna to transmit on.", metavar="ANT")

    (options, args) = parser.parse_args()

    mandatories = ['msg', 'frequency', 'wpm', 'dev']
    for m in mandatories:
        if options.__dict__[m] is None:
            print("You forgot an arguement")
            parser.print_help()
            exit(-1)
    main(options.msg, options.wpm, options.frequency, options.dev, options.ant)
