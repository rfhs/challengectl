#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Freq Hopper
# Author: Corey Koval
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
from math import pi
import fhss_tx_hop_set as hop_set  # embedded python module
import osmosdr
import time




class fhss_tx(gr.top_block):

    def __init__(self, bb_gain=20, channel_spacing=100e3, dev='bladerf=0', file='./test.wav', freq=int(449e6), hop_rate=10, hop_time=60, if_gain=20, ppm=0, rf_gain=20, rf_rate=2000000, seed='RFHS', wav_rate=48000):
        gr.top_block.__init__(self, "Freq Hopper", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.bb_gain = bb_gain
        self.channel_spacing = channel_spacing
        self.dev = dev
        self.file = file
        self.freq = freq
        self.hop_rate = hop_rate
        self.hop_time = hop_time
        self.if_gain = if_gain
        self.ppm = ppm
        self.rf_gain = rf_gain
        self.rf_rate = rf_rate
        self.seed = seed
        self.wav_rate = wav_rate

        ##################################################
        # Variables
        ##################################################
        self.rand_low = rand_low = -(((rf_rate/2)-channel_spacing)/channel_spacing)
        self.rand_high = rand_high = (((rf_rate/2)-channel_spacing)/channel_spacing)
        self.audio_rate = audio_rate = 48000
        self.temp_hops = temp_hops = [-3,-2,-1,0,1,2,3]
        self.num_channels = num_channels = ((((rf_rate/2)-channel_spacing)/channel_spacing)*2)+1
        self.if_rate = if_rate = audio_rate*4
        self.hopset = hopset = hop_set.mkhopset(seed,rand_low,rand_high,hop_rate,hop_time)

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=audio_rate,
                decimation=wav_rate,
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=rf_rate,
                decimation=if_rate,
                taps=[],
                fractional_bw=0)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + dev
        )
        self.osmosdr_sink_0.set_sample_rate(rf_rate)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(ppm, 0)
        self.osmosdr_sink_0.set_gain(rf_gain, 0)
        self.osmosdr_sink_0.set_if_gain(if_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                rf_rate,
                3e3,
                2e3,
                window.WIN_HAMMING,
                6.76))
        self.blocks_wavfile_source_0 = blocks.wavfile_source(file, False)
        self.blocks_vector_source_x_0 = blocks.vector_source_f(hopset, True, 1, [])
        self.blocks_vco_c_0 = blocks.vco_c(rf_rate, 2*pi*channel_spacing, 1)
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_float*1, int(rf_rate*(1/hop_rate)))
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
        	audio_rate=audio_rate,
        	quad_rate=if_rate,
        	tau=75e-6,
        	max_dev=5e3,
        	fh=-1.0,
                )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_tx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_vco_c_0, 0))
        self.connect((self.blocks_vco_c_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.rational_resampler_xxx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.analog_nbfm_tx_0, 0))


    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self.osmosdr_sink_0.set_bb_gain(self.bb_gain, 0)

    def get_channel_spacing(self):
        return self.channel_spacing

    def set_channel_spacing(self, channel_spacing):
        self.channel_spacing = channel_spacing
        self.set_num_channels(((((self.rf_rate/2)-self.channel_spacing)/self.channel_spacing)*2)+1)
        self.set_rand_high((((self.rf_rate/2)-self.channel_spacing)/self.channel_spacing))
        self.set_rand_low(-(((self.rf_rate/2)-self.channel_spacing)/self.channel_spacing))

    def get_dev(self):
        return self.dev

    def set_dev(self, dev):
        self.dev = dev

    def get_file(self):
        return self.file

    def set_file(self, file):
        self.file = file

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)

    def get_hop_rate(self):
        return self.hop_rate

    def set_hop_rate(self, hop_rate):
        self.hop_rate = hop_rate
        self.set_hopset(hop_set.mkhopset(self.seed,self.rand_low,self.rand_high,self.hop_rate,self.hop_time))
        self.blocks_repeat_0.set_interpolation(int(self.rf_rate*(1/self.hop_rate)))

    def get_hop_time(self):
        return self.hop_time

    def set_hop_time(self, hop_time):
        self.hop_time = hop_time
        self.set_hopset(hop_set.mkhopset(self.seed,self.rand_low,self.rand_high,self.hop_rate,self.hop_time))

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_sink_0.set_if_gain(self.if_gain, 0)

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

    def get_rf_rate(self):
        return self.rf_rate

    def set_rf_rate(self, rf_rate):
        self.rf_rate = rf_rate
        self.set_num_channels(((((self.rf_rate/2)-self.channel_spacing)/self.channel_spacing)*2)+1)
        self.set_rand_high((((self.rf_rate/2)-self.channel_spacing)/self.channel_spacing))
        self.set_rand_low(-(((self.rf_rate/2)-self.channel_spacing)/self.channel_spacing))
        self.blocks_repeat_0.set_interpolation(int(self.rf_rate*(1/self.hop_rate)))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.rf_rate, 3e3, 2e3, window.WIN_HAMMING, 6.76))
        self.osmosdr_sink_0.set_sample_rate(self.rf_rate)

    def get_seed(self):
        return self.seed

    def set_seed(self, seed):
        self.seed = seed
        self.set_hopset(hop_set.mkhopset(self.seed,self.rand_low,self.rand_high,self.hop_rate,self.hop_time))

    def get_wav_rate(self):
        return self.wav_rate

    def set_wav_rate(self, wav_rate):
        self.wav_rate = wav_rate

    def get_rand_low(self):
        return self.rand_low

    def set_rand_low(self, rand_low):
        self.rand_low = rand_low
        self.set_hopset(hop_set.mkhopset(self.seed,self.rand_low,self.rand_high,self.hop_rate,self.hop_time))

    def get_rand_high(self):
        return self.rand_high

    def set_rand_high(self, rand_high):
        self.rand_high = rand_high
        self.set_hopset(hop_set.mkhopset(self.seed,self.rand_low,self.rand_high,self.hop_rate,self.hop_time))

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.set_if_rate(self.audio_rate*4)

    def get_temp_hops(self):
        return self.temp_hops

    def set_temp_hops(self, temp_hops):
        self.temp_hops = temp_hops

    def get_num_channels(self):
        return self.num_channels

    def set_num_channels(self, num_channels):
        self.num_channels = num_channels

    def get_if_rate(self):
        return self.if_rate

    def set_if_rate(self, if_rate):
        self.if_rate = if_rate

    def get_hopset(self):
        return self.hopset

    def set_hopset(self, hopset):
        self.hopset = hopset
        self.blocks_vector_source_x_0.set_data(self.hopset, [])



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "-b", "--bb-gain", dest="bb_gain", type=eng_float, default=eng_notation.num_to_str(float(20)),
        help="Set Base Band Gain [default=%(default)r]")
    parser.add_argument(
        "-c", "--channel-spacing", dest="channel_spacing", type=eng_float, default=eng_notation.num_to_str(float(100e3)),
        help="Set Channel Spacing [default=%(default)r]")
    parser.add_argument(
        "-d", "--dev", dest="dev", type=str, default='bladerf=0',
        help="Set Device String [default=%(default)r]")
    parser.add_argument(
        "-w", "--file", dest="file", type=str, default='./test.wav',
        help="Set Wav File [default=%(default)r]")
    parser.add_argument(
        "-f", "--freq", dest="freq", type=intx, default=int(449e6),
        help="Set Center Frequency [default=%(default)r]")
    parser.add_argument(
        "--hop-rate", dest="hop_rate", type=intx, default=10,
        help="Set Hops per second [default=%(default)r]")
    parser.add_argument(
        "--hop-time", dest="hop_time", type=eng_float, default=eng_notation.num_to_str(float(60)),
        help="Set Seconds of Non-Repeating Hop Data [default=%(default)r]")
    parser.add_argument(
        "-i", "--if-gain", dest="if_gain", type=eng_float, default=eng_notation.num_to_str(float(20)),
        help="Set IF Gain [default=%(default)r]")
    parser.add_argument(
        "-p", "--ppm", dest="ppm", type=intx, default=0,
        help="Set PPM [default=%(default)r]")
    parser.add_argument(
        "-g", "--rf-gain", dest="rf_gain", type=eng_float, default=eng_notation.num_to_str(float(20)),
        help="Set RF Gain [default=%(default)r]")
    parser.add_argument(
        "-r", "--rf-rate", dest="rf_rate", type=intx, default=2000000,
        help="Set RF Sample Rate [default=%(default)r]")
    parser.add_argument(
        "-s", "--seed", dest="seed", type=str, default='RFHS',
        help="Set Seed [default=%(default)r]")
    parser.add_argument(
        "-r", "--wav-rate", dest="wav_rate", type=intx, default=48000,
        help="Set Wav File Sample Rate [default=%(default)r]")
    return parser


def main(top_block_cls=fhss_tx, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(bb_gain=options.bb_gain, channel_spacing=options.channel_spacing, dev=options.dev, file=options.file, freq=options.freq, hop_rate=options.hop_rate, hop_time=options.hop_time, if_gain=options.if_gain, ppm=options.ppm, rf_gain=options.rf_gain, rf_rate=options.rf_rate, seed=options.seed, wav_rate=options.wav_rate)

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
