#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Cw
# Generated: Fri Jul 21 21:59:55 2017
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import SimpleXMLRPCServer
import osmosdr
import threading
import time

morse_code='0,'
morse=()
wpm=1
freq=0
dev="0a"

class cw(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Cw")

        ##################################################
        # Variables
        ##################################################
        self.wpm = wpm
        self.samp_rate = samp_rate = 48000
        self.morse = morse
        self.freq = freq
        self.amp = amp = 1

        ##################################################
        # Blocks
        ##################################################
        self.xmlrpc_server_0 = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", 8080), allow_none=True)
        self.xmlrpc_server_0.register_instance(self)
        self.xmlrpc_server_0_thread = threading.Thread(target=self.xmlrpc_server_0.serve_forever)
        self.xmlrpc_server_0_thread.daemon = True
        self.xmlrpc_server_0_thread.start()
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=2000000,
                decimation=samp_rate,
                taps=None,
                fractional_bw=None,
        )
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + str(dev) )
        self.osmosdr_sink_0.set_sample_rate(2000000)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(37, 0)
        self.osmosdr_sink_0.set_if_gain(32, 0)
        self.osmosdr_sink_0.set_bb_gain(32, 0)
        self.osmosdr_sink_0.set_antenna("", 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self.blocks_vector_source_x_0 = blocks.vector_source_c(morse, False, 1, [])
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex*1, wpm*100)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 700, amp, 0)

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
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)

    def get_amp(self):
        return self.amp

    def set_amp(self, amp):
        self.amp = amp
        self.analog_sig_source_x_0.set_amplitude(self.amp)


def main(mesg, wordspm, frequency, device, top_block_cls=cw, options=None):

    global morse
    global wpm
    global freq
    global dev

    wpm = wordspm
    freq = frequency
    dev = device

    morse_code='0,'

    scale = 16
    num_of_bits = 8
    str1=bin(int(mesg, scale))[2:].zfill(num_of_bits)
    tmp = ','.join(list(str1))
    morse_code=morse_code+tmp+',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'

    morse_split=morse_code.split(',')

    morse=map(int,morse_split)*10

    morse_code=morse_code+'0,0,0,0,0,0,0,0,0,0,0'

    m_split=morse_code.split(',')

    morse=map(int,m_split)

    tb = top_block_cls()
    tb.start()
    tb.wait()

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

    (options, args) = parser.parse_args()

    mandatories = ['msg', 'frequency', 'wpm', 'dev']
    for m in mandatories:
      if options.__dict__[m] is None:
        print "You forgot an arguement"
        parser.print_help()
        exit(-1)

    main(options.msg, options.wpm, options.frequency, options.dev)
