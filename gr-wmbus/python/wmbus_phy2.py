#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Wmbus Phy2
# Generated: Sat Oct 13 16:36:00 2012
##################################################

from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from optparse import OptionParser

class wmbus_phy2(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Wmbus Phy2")

		##################################################
		# Variables
		##################################################
		self.frame = frame = [1,1]

		##################################################
		# Blocks
		##################################################
		self.gr_vector_source_x_0 = gr.vector_source_b((frame), False, 1)
		self.gr_vector_sink_x_1 = gr.vector_sink_b(1)
		self.gr_vector_sink_x_0 = gr.vector_sink_b(1)
		self.gr_unpacked_to_packed_xx_0 = gr.unpacked_to_packed_bb(4, gr.GR_MSB_FIRST)
		self.gr_pack_k_bits_bb_0 = gr.pack_k_bits_bb(6)
		self.digital_map_bb_1 = digital.map_bb(([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]))
		self.digital_map_bb_0 = digital.map_bb(([16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 3, 16, 1, 2, 16, 16, 16, 16, 7, 16, 16, 0, 16, 16, 5, 6, 16, 4, 16, 16, 16, 16, 16, 16, 11, 16, 9, 10, 16, 16, 15, 16, 16, 8, 16, 16, 16, 16, 13, 14, 16, 12, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16]))

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_vector_source_x_0, 0), (self.gr_pack_k_bits_bb_0, 0))
		self.connect((self.gr_pack_k_bits_bb_0, 0), (self.digital_map_bb_0, 0))
		self.connect((self.digital_map_bb_0, 0), (self.gr_unpacked_to_packed_xx_0, 0))
		self.connect((self.gr_unpacked_to_packed_xx_0, 0), (self.gr_vector_sink_x_0, 0))
		self.connect((self.digital_map_bb_0, 0), (self.digital_map_bb_1, 0))
		self.connect((self.digital_map_bb_1, 0), (self.gr_vector_sink_x_1, 0))

	def get_frame(self):
		return self.frame

	def set_frame(self, frame):
		self.frame = frame

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = wmbus_phy2()
	tb.run()

