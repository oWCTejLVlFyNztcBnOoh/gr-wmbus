#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Wmbus Phy1
# Generated: Sat Oct 13 16:01:50 2012
##################################################

from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.gr import firdes
import wmbus_blocks as mbus
from wmbus.wmbus_demod import *   

class wmbus_phy1(gr.hier_block2):

	def __init__(self, samp_rate=1600000, samp_per_sym=16, verbose=0, msgq=0, freq_error=-0.0025000):
		gr.hier_block2.__init__(
			self, "Wmbus Phy1",
			gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
			gr.io_signature(0, 0, 0),
		)

		##################################################
		# Parameters
		##################################################
		self.samp_rate = samp_rate
		self.samp_per_sym = samp_per_sym
		self.verbose = verbose
		self.msgq = msgq
		self.freq_error = freq_error

		##################################################
		# Blocks
		##################################################
		self.wmbus_demod_0 = wmbus_demod(
			samp_rate=1600000,
			samp_per_sym=16,
			freq_error=-0.0025000,
		)
		self.gr_nlog10_ff_0 = gr.nlog10_ff(10, 1, 0)
		self.gr_complex_to_mag_squared_0 = gr.complex_to_mag_squared(1)
		self.fir_filter_xxx_0 = filter.fir_filter_fff(samp_per_sym, (16*[1./16]))
		self.any_sink_0_1 = mbus.framer(msgq, verbose) 
		self.any_0 = mbus.correlate_preamble()

		##################################################
		# Connections
		##################################################
		self.connect((self.any_0, 0), (self.any_sink_0_1, 0))
		self.connect((self.gr_complex_to_mag_squared_0, 0), (self.gr_nlog10_ff_0, 0))
		self.connect((self.gr_nlog10_ff_0, 0), (self.fir_filter_xxx_0, 0))
		self.connect((self.fir_filter_xxx_0, 0), (self.any_sink_0_1, 1))
		self.connect((self, 0), (self.gr_complex_to_mag_squared_0, 0))
		self.connect((self, 0), (self.wmbus_demod_0, 0))
		self.connect((self.wmbus_demod_0, 0), (self.any_0, 0))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def get_samp_per_sym(self):
		return self.samp_per_sym

	def set_samp_per_sym(self, samp_per_sym):
		self.samp_per_sym = samp_per_sym

	def get_verbose(self):
		return self.verbose

	def set_verbose(self, verbose):
		self.verbose = verbose

	def get_msgq(self):
		return self.msgq

	def set_msgq(self, msgq):
		self.msgq = msgq

	def get_freq_error(self):
		return self.freq_error

	def set_freq_error(self, freq_error):
		self.freq_error = freq_error


