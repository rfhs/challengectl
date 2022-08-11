#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Nbfm
# GNU Radio version: 3.7.13.5
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
# from optparse import OptionParser
import configparser
import osmosdr
import time


class nbfm(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Nbfm")

        ##################################################
        # Variables
        ##################################################
        self.filename = filename = "nbfm_tx.conf"
        # self.wav_samp_rate = wav_samp_rate = 48000
        # self.wav_file = wav_file = ""
        self._samp_rate_config = configparser.ConfigParser()
        self._samp_rate_config.read(filename)
        try:
            samp_rate = self._samp_rate_config.getint('main', 'samp_rate')
        except:
            samp_rate = int(2.4e6)
        self.samp_rate = samp_rate
        self._rf_gain_config = configparser.ConfigParser()
        self._rf_gain_config.read(filename)
        try:
            rf_gain = self._rf_gain_config.getfloat('main', 'tx_rf_gain')
        except:
            rf_gain = 43
        print(f"RF Gain: {rf_gain}")
        self.rf_gain = rf_gain
        self._if_gain_config = configparser.ConfigParser()
        self._if_gain_config.read(filename)
        try:
            if_gain = self._if_gain_config.getfloat('main', 'tx_if_gain')
        except:
            if_gain = 32
        self.if_gain = if_gain
        # self.freq = freq = 0
        # self.dev = dev = ""
        self._bb_gain_config = configparser.ConfigParser()
        self._bb_gain_config.read(filename)
        try:
            bb_gain = self._bb_gain_config.getfloat('main', 'tx_bb_gain')
        except:
            bb_gain = 32
        self.bb_gain = bb_gain

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
            interpolation=samp_rate,
            decimation=int(240e3),
            taps=None,
            fractional_bw=None,
        )
        self.osmosdr_sink_0 = osmosdr.sink(args="numchan=" + str(1) + " " + str(dev))
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(25, 0)
        self.osmosdr_sink_0.set_gain(rf_gain, 0)
        self.osmosdr_sink_0.set_if_gain(if_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self.blocks_wavfile_source_0 = blocks.wavfile_source(wav_file, False)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((0.7, ))
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
            audio_rate=wav_samp_rate,
            quad_rate=int(240e3),
            tau=75e-6,
            max_dev=5e3,
            fh=-1.0,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_tx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.analog_nbfm_tx_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        self.filename = filename
        self._samp_rate_config = configparser.ConfigParser()
        self._samp_rate_config.read(self.filename)
        if not self._samp_rate_config.has_section('main'):
            self._samp_rate_config.add_section('main')

        self._samp_rate_config.set('main', 'samp_rate', str(None))
        self._samp_rate_config.write(open(self.filename, 'w'))
        self._rf_gain_config = configparser.ConfigParser()
        self._rf_gain_config.read(self.filename)
        if not self._rf_gain_config.has_section('main'):
            self._rf_gain_config.add_section('main')

        self._rf_gain_config.set('main', 'tx_rf_gain', str(None))
        self._rf_gain_config.write(open(self.filename, 'w'))
        self._if_gain_config = configparser.ConfigParser()
        self._if_gain_config.read(self.filename)
        if not self._if_gain_config.has_section('main'):
            self._if_gain_config.add_section('main')

        self._if_gain_config.set('main', 'tx_if_gain', str(None))
        self._if_gain_config.write(open(self.filename, 'w'))
        self._bb_gain_config = configparser.ConfigParser()
        self._bb_gain_config.read(self.filename)
        if not self._bb_gain_config.has_section('main'):
            self._bb_gain_config.add_section('main')

        self._bb_gain_config.set('main', 'tx_bb_gain', str(None))
        self._bb_gain_config.write(open(self.filename, 'w'))

    def get_wav_samp_rate(self):
        return self.wav_samp_rate

    def set_wav_samp_rate(self, wav_samp_rate):
        self.wav_samp_rate = wav_samp_rate

    def get_wav_file(self):
        return self.wav_file

    def set_wav_file(self, wav_file):
        self.wav_file = wav_file

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.osmosdr_sink_0.set_gain(self.rf_gain, 0)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_sink_0.set_if_gain(self.if_gain, 0)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)

    def get_dev(self):
        return self.dev

    def set_dev(self, dev):
        self.dev = dev

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self.osmosdr_sink_0.set_bb_gain(self.bb_gain, 0)


def main(wav_src, wav_rate, frequency, device, top_block_cls=nbfm, options=None):

    global wav_file
    global wav_samp_rate
    global freq
    global dev

    wav_file = wav_src
    wav_samp_rate = wav_rate
    freq = frequency
    dev = device

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
