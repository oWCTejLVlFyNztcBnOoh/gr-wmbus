#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Wireless M-Bus Demod
# Generated: Sat Oct 13 15:58:56 2012
##################################################

from gnuradio import digital
from gnuradio import gr
from gnuradio.gr import firdes

class wmbus_demod(gr.hier_block2):

	def __init__(self, samp_rate=1600000, samp_per_sym=16, freq_error=-0.0025000):
		gr.hier_block2.__init__(
			self, "Wireless M-Bus Demod",
			gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
			gr.io_signature(1, 1, gr.sizeof_char*1),
		)

		##################################################
		# Parameters
		##################################################
		self.samp_rate = samp_rate
		self.samp_per_sym = samp_per_sym
		self.freq_error = freq_error

		##################################################
		# Variables
		##################################################
		self.cutoff = cutoff = 120e3
		self.chip_rate = chip_rate = samp_rate/samp_per_sym

		##################################################
		# Blocks
		##################################################
		self.low_pass_filter_0 = gr.fir_filter_ccf(1, firdes.low_pass(
			1, samp_rate, cutoff, cutoff/2, firdes.WIN_HAMMING, 6.76))
		self.gr_sub_xx_0 = gr.sub_ff(1)
		self.gr_single_pole_iir_filter_xx_0 = gr.single_pole_iir_filter_ff(0.0512/samp_per_sym, 1)
		self.gr_quadrature_demod_cf_0 = gr.quadrature_demod_cf(1)
		self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_ff(samp_per_sym*(1+freq_error), .25 *0.06*0.06*4, 0.5, 0.06*2, 0.002*2)
		self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_quadrature_demod_cf_0, 0), (self.gr_single_pole_iir_filter_xx_0, 0))
		self.connect((self.gr_single_pole_iir_filter_xx_0, 0), (self.gr_sub_xx_0, 1))
		self.connect((self.gr_quadrature_demod_cf_0, 0), (self.gr_sub_xx_0, 0))
		self.connect((self.gr_sub_xx_0, 0), (self.digital_clock_recovery_mm_xx_0, 0))
		self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.gr_quadrature_demod_cf_0, 0))
		self.connect((self.digital_binary_slicer_fb_0, 0), (self, 0))
		self.connect((self, 0), (self.low_pass_filter_0, 0))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.set_chip_rate(self.samp_rate/self.samp_per_sym)
		self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff, self.cutoff/2, firdes.WIN_HAMMING, 6.76))

	def get_samp_per_sym(self):
		return self.samp_per_sym

	def set_samp_per_sym(self, samp_per_sym):
		self.samp_per_sym = samp_per_sym
		self.set_chip_rate(self.samp_rate/self.samp_per_sym)
		self.gr_single_pole_iir_filter_xx_0.set_taps(0.0512/self.samp_per_sym)
		self.digital_clock_recovery_mm_xx_0.set_omega(self.samp_per_sym*(1+self.freq_error))

	def get_freq_error(self):
		return self.freq_error

	def set_freq_error(self, freq_error):
		self.freq_error = freq_error
		self.digital_clock_recovery_mm_xx_0.set_omega(self.samp_per_sym*(1+self.freq_error))

	def get_cutoff(self):
		return self.cutoff

	def set_cutoff(self, cutoff):
		self.cutoff = cutoff
		self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff, self.cutoff/2, firdes.WIN_HAMMING, 6.76))

	def get_chip_rate(self):
		return self.chip_rate

	def set_chip_rate(self, chip_rate):
		self.chip_rate = chip_rate


