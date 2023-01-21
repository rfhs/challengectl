#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: USB TX
# Author: K3CPK
# Description: USB transmitter using complex band pass filter.
# GNU Radio version: 3.7.13.5
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.fft import window
# from optparse import OptionParser
import configparser
import osmosdr
import time


class usb_tx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "USB TX")

        ##################################################
        # Variables
        ##################################################
        self.low = low = 300
        self.filter_width = filter_width = 2.7e3
        self.file_name = file_name = "usb_tx.conf"
        #self.wav_samp_rate = wav_samp_rate = 48000
#        self.wav_file = wav_file = ""
        self._rf_samp_rate_config = configparser.ConfigParser()
        self._rf_samp_rate_config.read(file_name)
        try:
            rf_samp_rate = self._rf_samp_rate_config.getfloat('tx', 'rf_samp_rate')
        except:
            rf_samp_rate = 2e6
        self.rf_samp_rate = rf_samp_rate
        self._rf_gain_config = configparser.ConfigParser()
        self._rf_gain_config.read(file_name)
        try:
            rf_gain = self._rf_gain_config.getfloat('tx', 'tx_rf_gain')
        except:
            rf_gain = 43
        print(f"RF Gain: {rf_gain}")
        self.rf_gain = rf_gain
        self._offset_config = configparser.ConfigParser()
        self._offset_config.read(file_name)
        try:
            offset = self._offset_config.getfloat('tx', 'offset')
        except:
            offset = 5e3
        self.offset = offset
        self._if_samp_rate_config = configparser.ConfigParser()
        self._if_samp_rate_config.read(file_name)
        try:
            if_samp_rate = self._if_samp_rate_config.getfloat('tx', 'if_samp_rate')
        except:
            if_samp_rate = 48e3
        self.if_samp_rate = if_samp_rate
        self._if_gain_config = configparser.ConfigParser()
        self._if_gain_config.read(file_name)
        try:
            if_gain = self._if_gain_config.getfloat('tx', 'tx_if_gain')
        except:
            if_gain = 20
        self.if_gain = if_gain
        self.high = high = low + filter_width
        #self.freq = freq = 0
        #self.dev = dev = 0
        self._carrier_level_config = configparser.ConfigParser()
        self._carrier_level_config.read(file_name)
        try:
            carrier_level = self._carrier_level_config.getfloat('tx', 'carrier_level')
        except:
            carrier_level = 1
        self.carrier_level = carrier_level
        self._bb_gain_config = configparser.ConfigParser()
        self._bb_gain_config.read(file_name)
        try:
            bb_gain = self._bb_gain_config.getfloat('tx', 'tx_bb_gain')
        except:
            bb_gain = 20
        self.bb_gain = bb_gain
        self._audio_gain_config = configparser.ConfigParser()
        self._audio_gain_config.read(file_name)
        try:
            audio_gain = self._audio_gain_config.getfloat('tx', 'audio_gain')
        except:
            audio_gain = 600e-3
        self.audio_gain = audio_gain

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_ccc(
            interpolation=int(rf_samp_rate),
            decimation=int(if_samp_rate),
            taps=[],
            fractional_bw=0.0,
        )
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
            interpolation=int(if_samp_rate),
            decimation=int(wav_samp_rate),
            taps=[],
            fractional_bw=0.0,
        )
        self.osmosdr_sink_0 = osmosdr.sink(args="numchan=" + str(1) + " " + str(dev))
        self.osmosdr_sink_0.set_sample_rate(rf_samp_rate)
        self.osmosdr_sink_0.set_center_freq(freq - offset, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(rf_gain, 0)
        self.osmosdr_sink_0.set_if_gain(if_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self.blocks_wavfile_source_0 = blocks.wavfile_source(wav_file, False)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((audio_gain, ))
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.band_pass_filter_0 = filter.interp_fir_filter_ccc(1, firdes.complex_band_pass(
            1, if_samp_rate, low, high, 100, window.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0_0 = analog.sig_source_c(if_samp_rate, analog.GR_COS_WAVE, offset, 1, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(if_samp_rate, analog.GR_SIN_WAVE, 0, carrier_level, 0)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.band_pass_filter_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.osmosdr_sink_0, 0))

    def get_low(self):
        return self.low

    def set_low(self, low):
        self.low = low
        self.set_high(self.low + self.filter_width)
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, self.low, self.high, 100, window.WIN_HAMMING, 6.76))

    def get_filter_width(self):
        return self.filter_width

    def set_filter_width(self, filter_width):
        self.filter_width = filter_width
        self.set_high(self.low + self.filter_width)

    def get_file_name(self):
        return self.file_name

    def set_file_name(self, file_name):
        self.file_name = file_name
        self._rf_samp_rate_config = configparser.ConfigParser()
        self._rf_samp_rate_config.read(self.file_name)
        if not self._rf_samp_rate_config.has_section('tx'):
            self._rf_samp_rate_config.add_section('tx')
        self._rf_samp_rate_config.set('tx', 'rf_samp_rate', str(None))
        self._rf_samp_rate_config.write(open(self.file_name, 'w'))
        self._rf_gain_config = configparser.ConfigParser()
        self._rf_gain_config.read(self.file_name)
        if not self._rf_gain_config.has_section('tx'):
            self._rf_gain_config.add_section('tx')
        self._rf_gain_config.set('tx', 'tx_rf_gain', str(None))
        self._rf_gain_config.write(open(self.file_name, 'w'))
        self._offset_config = configparser.ConfigParser()
        self._offset_config.read(self.file_name)
        if not self._offset_config.has_section('tx'):
            self._offset_config.add_section('tx')
        self._offset_config.set('tx', 'offset', str(None))
        self._offset_config.write(open(self.file_name, 'w'))
        self._if_samp_rate_config = configparser.ConfigParser()
        self._if_samp_rate_config.read(self.file_name)
        if not self._if_samp_rate_config.has_section('tx'):
            self._if_samp_rate_config.add_section('tx')
        self._if_samp_rate_config.set('tx', 'if_samp_rate', str(None))
        self._if_samp_rate_config.write(open(self.file_name, 'w'))
        self._if_gain_config = configparser.ConfigParser()
        self._if_gain_config.read(self.file_name)
        if not self._if_gain_config.has_section('tx'):
            self._if_gain_config.add_section('tx')
        self._if_gain_config.set('tx', 'tx_if_gain', str(None))
        self._if_gain_config.write(open(self.file_name, 'w'))
        self._carrier_level_config = configparser.ConfigParser()
        self._carrier_level_config.read(self.file_name)
        if not self._carrier_level_config.has_section('tx'):
            self._carrier_level_config.add_section('tx')
        self._carrier_level_config.set('tx', 'carrier_level', str(None))
        self._carrier_level_config.write(open(self.file_name, 'w'))
        self._bb_gain_config = configparser.ConfigParser()
        self._bb_gain_config.read(self.file_name)
        if not self._bb_gain_config.has_section('tx'):
            self._bb_gain_config.add_section('tx')
        self._bb_gain_config.set('tx', 'tx_bb_gain', str(None))
        self._bb_gain_config.write(open(self.file_name, 'w'))
        self._audio_gain_config = configparser.ConfigParser()
        self._audio_gain_config.read(self.file_name)
        if not self._audio_gain_config.has_section('tx'):
            self._audio_gain_config.add_section('tx')
        self._audio_gain_config.set('tx', 'audio_gain', str(None))
        self._audio_gain_config.write(open(self.file_name, 'w'))

    def get_wav_samp_rate(self):
        return self.wav_samp_rate

    def set_wav_samp_rate(self, wav_samp_rate):
        self.wav_samp_rate = wav_samp_rate

    def get_wav_file(self):
        return self.wav_file

    def set_wav_file(self, wav_file):
        self.wav_file = wav_file

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        self.rf_samp_rate = rf_samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.rf_samp_rate)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.osmosdr_sink_0.set_gain(self.rf_gain, 0)

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.osmosdr_sink_0.set_center_freq(self.freq - self.offset, 0)
        self.analog_sig_source_x_0_0.set_frequency(self.offset)

    def get_if_samp_rate(self):
        return self.if_samp_rate

    def set_if_samp_rate(self, if_samp_rate):
        self.if_samp_rate = if_samp_rate
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, self.low, self.high, 100, window.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0_0.set_sampling_freq(self.if_samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.if_samp_rate)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_sink_0.set_if_gain(self.if_gain, 0)

    def get_high(self):
        return self.high

    def set_high(self, high):
        self.high = high
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, self.low, self.high, 100, window.WIN_HAMMING, 6.76))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq - self.offset, 0)

    def get_dev(self):
        return self.dev

    def set_dev(self, dev):
        self.dev = dev

    def get_carrier_level(self):
        return self.carrier_level

    def set_carrier_level(self, carrier_level):
        self.carrier_level = carrier_level
        self.analog_sig_source_x_0.set_amplitude(self.carrier_level)

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self.osmosdr_sink_0.set_bb_gain(self.bb_gain, 0)

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_vxx_0.set_k((self.audio_gain, ))


def main(wav_src, wav_rate, frequency, device, top_block_cls=usb_tx, options=None):

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
