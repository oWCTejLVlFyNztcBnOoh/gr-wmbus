#!/usr/bin/env python

import numpy
from gnuradio import gr 
from gnuradio.extras import block_gateway
from gnuradio import digital
from gnuradio.digital import packet_utils
from optparse import OptionParser
from gnuradio.eng_option import eng_option
from gruel.pmt.pmt_swig import pmt_print
from gnuradio.extras.extras_swig import pmt_symbol_to_string
from numpy.numarray.functions import ones

class correlate_preamble(gr.hier_block2): 
    """
    The total preamble (header + synchronisation) chips sequence for this mode shall 
    be nx(01) 0000111101 with n  >=  19.
    """
    
    def __init__(self, preamble="010101010", sync_word="0000111101"):
        """
        @param preamble: the preamble chips
        @param sync_word: the sync word bits
        """
        gr.hier_block2.__init__(
            self, "correlate_preamble",
            gr.io_signature(1, 1, gr.sizeof_char*1),
            gr.io_signature(1, 1, gr.sizeof_char*1),
        )
        
        if not packet_utils.is_1_0_string(preamble):
            raise ValueError, "Invalid access_code %r. Must be string of 1's and 0's" % (preamble,)
        self.preamble = digital.correlate_access_code_tag_bb(preamble, 0, "preamble")

        if not packet_utils.is_1_0_string(sync_word):
            raise ValueError, "Invalid access_code %r. Must be string of 1's and 0's" % (sync_word,)
        self.sync = digital.correlate_access_code_tag_bb(sync_word, 0, "sync")

        self.connect(self, self.sync, self.preamble, self)


class framer(gr.block):

    def __init__(self, msgq, verbose=0):
        gr.block.__init__(
            self,
            name = "framer",
            in_sig = [numpy.uint8, numpy.float32],
            out_sig = None, #[numpy.uint8],
        )
        self.state = 0;
        self.power_drops = 0
        self.msgq = msgq
        self.pkt = ones(10000, dtype=numpy.uint8) 
        self.pos_write = 0
        self.preamble_power = 0
        self.power_threshold = 9
        self.power_drop_threshold = 6*8
        self.debug = (verbose > 2);
        

    def work(self, input_items, output_items):
        nread = self.nitems_read(0) #number of items read on port 0
        ninput_items = len(input_items[0])

        #read all tags associated with port 0 for items in this work function
        tags = self.get_tags_in_range(0, nread, nread+ninput_items)

        #for ff in range(0,ninput_items):
        #    print (nread+ff, input_items[0][ff], input_items[1][ff])
        #    for tag in tags:
        #        if tag.offset == nread+ff:
        #            print pmt_symbol_to_string(tag.key)

        #work stuff here...
        pos_read = 0;
        for tag in tags:
            # process
            pos_read_end = tag.offset-nread
            self.process(input_items, pos_read, pos_read_end)
            pos_read = pos_read_end
            
            # state change
            tag_key = pmt_symbol_to_string(tag.key)
            if self.debug: print tag_key
            if tag_key == "preamble":
                self.state = 1
                self.preamble_power = input_items[1][nread-tag.offset]
                self.make_pkt()
            elif tag_key == "sync":
                self.state = 2
                self.make_pkt()

        pos_read_end = ninput_items
        self.process(input_items, pos_read, pos_read_end)
                
        return (ninput_items)

    def stop(self):
        self.make_pkt()
        return True

    def process(self, input_items, start, end):
        if self.state == 2:
            for i in range(start,end):
                if input_items[1][i] < self.preamble_power - self.power_threshold:
                    self.power_drops += 1
                else:
                    self.power_drops = 0
                if self.power_drops > self.power_drop_threshold:
                    end = i
                    self.state = 0
                    break;
            self.pkt[self.pos_write:self.pos_write+(end-start)] = input_items[0][start:end]
            self.pos_write += end-start
            if self.state == 0:
                if self.debug: print "carrier lost"
                self.make_pkt()

    def make_pkt(self):
        if self.pos_write > 0:
            msg = gr.message_from_string(self.pkt[0:self.pos_write].tostring(), 0, 0, 0);
            self.msgq.insert_tail(msg)
        self.pos_write = 0;
    
    
