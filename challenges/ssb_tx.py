#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SSB TX
# Author: Corey Koval
# Description: SSB transmitter using complex band pass filter.
# GNU Radio version: 3.10.1.1

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time




class ssb_tx(gr.top_block):

    def __init__(self, audio_gain=0.6, bb_gain=20, dev='hackrf=0', freq=445e6, if_gain=20, mode='usb', ppm=0, rf_gain=20, rf_samp_rate=2000000, wav_file='examples/example_voice.wav', wav_samp_rate=48000):
        gr.top_block.__init__(self, "SSB TX", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.audio_gain = audio_gain
        self.bb_gain = bb_gain
        self.dev = dev
        self.freq = freq
        self.if_gain = if_gain
        self.mode = mode
        self.ppm = ppm
        self.rf_gain = rf_gain
        self.rf_samp_rate = rf_samp_rate
        self.wav_file = wav_file
        self.wav_samp_rate = wav_samp_rate

        ##################################################
        # Variables
        ##################################################
        self.low = low = 300
        self.filter_width = filter_width = 2.7e3
        self.if_samp_rate = if_samp_rate = 48000
        self.high = high = low+filter_width
        self.carrier_level = carrier_level = 1

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_ccc(
                interpolation=int(rf_samp_rate),
                decimation=int(if_samp_rate),
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=int(if_samp_rate),
                decimation=int(wav_samp_rate),
                taps=[],
                fractional_bw=0)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + dev
        )
        self.osmosdr_sink_0.set_sample_rate(rf_samp_rate)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(ppm, 0)
        self.osmosdr_sink_0.set_gain(rf_gain, 0)
        self.osmosdr_sink_0.set_if_gain(if_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.blocks_wavfile_source_0 = blocks.wavfile_source(wav_file, False)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(audio_gain)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.band_pass_filter_0 = filter.interp_fir_filter_ccc(
            1,
            firdes.complex_band_pass(
                1,
                if_samp_rate,
                -high if mode == 'lsb' else low,
                -low if mode == 'lsb' else high,
                300,
                window.WIN_HAMMING,
                6.76))
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.band_pass_filter_0, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.osmosdr_sink_0, 0))


    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_vxx_0.set_k(self.audio_gain)

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self.osmosdr_sink_0.set_bb_gain(self.bb_gain, 0)

    def get_dev(self):
        return self.dev

    def set_dev(self, dev):
        self.dev = dev

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_sink_0.set_if_gain(self.if_gain, 0)

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, -self.high if self.mode == 'lsb' else self.low, -self.low if self.mode == 'lsb' else self.high, 300, window.WIN_HAMMING, 6.76))

    def get_ppm(self):
        return self.ppm

    def set_ppm(self, ppm):
        self.ppm = ppm
        self.osmosdr_sink_0.set_freq_corr(self.ppm, 0)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.osmosdr_sink_0.set_gain(self.rf_gain, 0)

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        self.rf_samp_rate = rf_samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.rf_samp_rate)

    def get_wav_file(self):
        return self.wav_file

    def set_wav_file(self, wav_file):
        self.wav_file = wav_file

    def get_wav_samp_rate(self):
        return self.wav_samp_rate

    def set_wav_samp_rate(self, wav_samp_rate):
        self.wav_samp_rate = wav_samp_rate

    def get_low(self):
        return self.low

    def set_low(self, low):
        self.low = low
        self.set_high(self.low+self.filter_width)
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, -self.high if self.mode == 'lsb' else self.low, -self.low if self.mode == 'lsb' else self.high, 300, window.WIN_HAMMING, 6.76))

    def get_filter_width(self):
        return self.filter_width

    def set_filter_width(self, filter_width):
        self.filter_width = filter_width
        self.set_high(self.low+self.filter_width)

    def get_if_samp_rate(self):
        return self.if_samp_rate

    def set_if_samp_rate(self, if_samp_rate):
        self.if_samp_rate = if_samp_rate
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, -self.high if self.mode == 'lsb' else self.low, -self.low if self.mode == 'lsb' else self.high, 300, window.WIN_HAMMING, 6.76))

    def get_high(self):
        return self.high

    def set_high(self, high):
        self.high = high
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.if_samp_rate, -self.high if self.mode == 'lsb' else self.low, -self.low if self.mode == 'lsb' else self.high, 300, window.WIN_HAMMING, 6.76))

    def get_carrier_level(self):
        return self.carrier_level

    def set_carrier_level(self, carrier_level):
        self.carrier_level = carrier_level



def argument_parser():
    description = 'SSB transmitter using complex band pass filter.'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--audio-gain", dest="audio_gain", type=eng_float, default=eng_notation.num_to_str(float(0.6)),
        help="Set Audio Gain [default=%(default)r]")
    parser.add_argument(
        "-b", "--bb-gain", dest="bb_gain", type=eng_float, default=eng_notation.num_to_str(float(20)),
        help="Set Base Band Gain [default=%(default)r]")
    parser.add_argument(
        "-d", "--dev", dest="dev", type=str, default='hackrf=0',
        help="Set Device String [default=%(default)r]")
    parser.add_argument(
        "-f", "--freq", dest="freq", type=eng_float, default=eng_notation.num_to_str(float(445e6)),
        help="Set Center Frequency [default=%(default)r]")
    parser.add_argument(
        "-i", "--if-gain", dest="if_gain", type=eng_float, default=eng_notation.num_to_str(float(20)),
        help="Set IF Gain [default=%(default)r]")
    parser.add_argument(
        "-m", "--mode", dest="mode", type=str, default='usb',
        help="Set Mode (usb or lsb) [default=%(default)r]")
    parser.add_argument(
        "-p", "--ppm", dest="ppm", type=intx, default=0,
        help="Set PPM [default=%(default)r]")
    parser.add_argument(
        "-g", "--rf-gain", dest="rf_gain", type=eng_float, default=eng_notation.num_to_str(float(20)),
        help="Set RF Gain [default=%(default)r]")
    parser.add_argument(
        "-r", "--rf-samp-rate", dest="rf_samp_rate", type=intx, default=2000000,
        help="Set RF Sample Rate [default=%(default)r]")
    parser.add_argument(
        "-w", "--wav-file", dest="wav_file", type=str, default='examples/example_voice.wav',
        help="Set Wav File [default=%(default)r]")
    parser.add_argument(
        "-a", "--wav-samp-rate", dest="wav_samp_rate", type=intx, default=48000,
        help="Set Wav Sample Rate [default=%(default)r]")
    return parser


def main(top_block_cls=ssb_tx, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(audio_gain=options.audio_gain, bb_gain=options.bb_gain, dev=options.dev, freq=options.freq, if_gain=options.if_gain, mode=options.mode, ppm=options.ppm, rf_gain=options.rf_gain, rf_samp_rate=options.rf_samp_rate, wav_file=options.wav_file, wav_samp_rate=options.wav_samp_rate)

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
