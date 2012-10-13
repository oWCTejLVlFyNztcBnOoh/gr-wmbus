#!/usr/bin/env python

import struct
from array import array
import numpy
from numpy.numarray.functions import ones
from optparse import OptionParser
from gnuradio import gr 
from gnuradio.extras import block_gateway
from gnuradio import digital
from gnuradio.digital import packet_utils
from gnuradio.eng_option import eng_option
from gruel.pmt.pmt_swig import pmt_print
from gnuradio.extras.extras_swig import pmt_symbol_to_string
import gnuradio.gr.gr_threading as _threading
import osmosdr
import crcmod.predefined
from wmbus.wmbus_phy1 import *
from wmbus.wmbus_phy2 import *

def to_hex(data, start=0, end=-1, format=2):
    s = ''
    if -1 == end:
        end = len(data)
    for i in range(start,end):
        if format == 2:
            s += ( "{:02X}".format(data[i]) )
        else: 
            s += ( "{:01X}".format(data[i]) )
    return s


def gen_map():
    map = [16] * 64
    coded = [22, 13, 14, 11, 28, 25, 26, 19, 44, 37, 38, 35, 52, 49, 50, 41]
    uncoded = range(0,16)
    for i in range(0,16):
        map[coded[i]] = uncoded[i]
    return map


class _queue_watcher_thread(_threading.Thread):
    def __init__(self, rcvd_pktq, callback):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.rcvd_pktq = rcvd_pktq
        self.callback = callback
        self.keep_running = True
        self.start()

    def run(self):
        while self.keep_running:
            msg = self.rcvd_pktq.delete_head()
            if self.callback:
                self.callback(msg)

class wmbus_pdu:
    def __init__(self, data, verbose=0):
        self.crc16 = crcmod.predefined.PredefinedCrc('crc-16-en-13757')
        data_len = len(data) 
        #print to_hex(data)
        
        # 5.5.2.2  Mode T: First block 
        # L-field  C-field  M-field  A-field  CRC-field 
        # 1 byte  1 byte  2 bytes  6 bytes  2 bytes
        self.decodeOk = True
        self.L = (data[0])
        self.C = (data[1])
        self.M = sum([data[2+i]*2**(i*8) for i in range(2)])
        #self.A = numpy.int8(data [4:10])
        self.A = to_hex(data[4:10]) #[hex(x) for x in data[4:10]]
        self.crc = sum([data[11-i]*2**(i*8) for i in range(2)])
        
        self.crc16.update(data[0:10])
        self.crcCalc = self.crc16.crcValue
        self.crcOk = (self.crcCalc == self.crc) 
        self.decodeOk = self.decodeOk and self.crcOk
        
        self.data = []
        self.datacrc = []
        self.datacrcCalc = []
        self.data1 = ''
        self.data1crc = 0
        self.data1crcCalc = 0
        
        L_left = self.L - 9 # fist block L and CRC are not counted

        self.ci = data[12]
        L_left -= 1
        d_start = 13
        d_end = d_start + min(L_left, 15)
        L_left -= 15  
        if d_end + 2 > data_len:
            if verbose > 1:
                print 'data truncated'
            self.decodeOk = False
            return
        self.data1 = to_hex(data[d_start:d_end]) #[hex(x) for x in data[d_start:d_end]]
        self.data1crc = sum([data[d_end+1-i]*2**(i*8) for i in range(2)])
        self.crc16 = crcmod.predefined.PredefinedCrc('crc-16-en-13757')
        self.crc16.update(data[12:d_end])
        self.data1crcCalc = self.crc16.crcValue
        self.decodeOk = self.decodeOk and (self.data1crcCalc == self.data1crc)
        
        while L_left > 0:
            d_start = d_end + 2
            d_end = d_start + min(L_left, 16)
            L_left -= 16
            #print to_hex(data[d_start:d_end])
            #print (data[d_start:d_end])
            #if True:
            #    self.crc16 = crcmod.predefined.PredefinedCrc('crc-16-en-13757')
            #    datadata = data[d_start:d_end]
            #    print to_hex(datadata)
            #    self.crc16.update(datadata)
            #    print '{:X}'.format(self.crc16.crcValue)
            if d_end + 2 > data_len:
                if verbose > 1:
                    print 'data truncated'
                self.decodeOk = False
                break
            self.data.append( to_hex(data[d_start:d_end]) )#[hex(x) for x in data[d_start:d_end]] )
            crc = sum([data[d_end+1-i]*2**(i*8) for i in range(2)])
            self.datacrc.append( crc )
            self.crc16 = crcmod.predefined.PredefinedCrc('crc-16-en-13757')
            self.crc16.update(data[d_start:d_end])
            self.datacrcCalc.append( self.crc16.crcValue )
            self.decodeOk = self.decodeOk and (self.crc16.crcValue ==crc)

    def __str__(self):
        #s = "[L:{:02X} C:{:02X} M:{:04X} A:{} crc:{:04X}]".format(self.L, self.C, self.M, self.A, self.crc)
        s = "[L:{:02X} C:{:02X} M:{:04X} A:{} crc:{:04X} {}]\n".format(self.L, self.C, self.M, self.A, self.crc, self.check_crc(self.crc,self.crcCalc)) 
        s += "[CI:{:02X} D:{} crc:{:04X} {}]\n".format(self.ci,self.data1,self.data1crc,self.check_crc(self.data1crc,self.data1crcCalc))
        for i in range(len(self.data)):
            s += "[D:{} crc:{:04X} {}]\n".format(self.data[i], self.datacrc[i], self.check_crc(self.datacrc[i], self.datacrcCalc[i]))
        return s
    
    def check_crc(self, crc_is, crc_should):
        if crc_is == crc_should:
            return 'ok'
        return "should:{:04X}".format(crc_should)
        

class wmbus_rx(gr.top_block):

    def __init__(self, filename=None, capture=None, verbose=False, freq_error=-0.0021875):
        gr.top_block.__init__(self) 
        self.verbose = verbose
        self.rx_chips_min = 16
        self.chip_error_threshold = 10

        if None != filename:
            self.source = gr.file_source(gr.sizeof_gr_complex, filename)
        else:
            self.source = osmosdr.source_c( args="nchan=" + str(1) + " " + "" )
            #print self.source.get_gain_range().to_pp_string()
            self.source.set_sample_rate(1.6e6)
            self.source.set_center_freq(868.95e6, 0)
            self.source.set_freq_corr(0, 0)
            self.source.set_gain_mode(0, 0)
            # -1.0 1.5 4.0 6.5 9.0 11.5 14.0 16.5 19.0 21.5 24.0 29.0 34.0 42.0
            self.source.set_gain(14, 0)
            self.source.set_if_gain(42, 0)

        if None != capture:
            self.sink = gr.file_sink(gr.sizeof_gr_complex, capture)
        else:
            self.msgq = gr.msg_queue(4)
            self.sink = wmbus_phy1(msgq=self.msgq, verbose=verbose, freq_error=freq_error);
            self._watcher = _queue_watcher_thread(self.msgq, self.callback)
        
        self.connect(self.source, self.sink)
        
        #self.msrc = gr.message_source(gr.sizeof_char, self.msgq)
        #self.mbus_phy2 = mbus_phy2();

        #self.connect(self.msrc, self.mbus_phy2)

        
    def callback(self, msg):
        vec = numpy.fromstring(msg.to_string(), numpy.uint8).tolist()
        phy2 = wmbus_phy2()
        phy2.gr_vector_source_x_0.set_data(vec)
        phy2.run()
        data = phy2.gr_vector_sink_x_0.data()
        err = phy2.gr_vector_sink_x_1.data()
        #dec_ok = (sum(err) < 5)#6*8)
        err_cnt = 0
        data2 = None
        for i in range(len(err)):
            err_cnt = err_cnt + err[i]
            if err_cnt > self.chip_error_threshold:
                data2 = data[0:i]
        if None == data2:
            data2 = data
        dec_ok = (len(data2) > self.rx_chips_min)
        
        if dec_ok:
            pdu = wmbus_pdu(array('B', data), self.verbose)
            if pdu.decodeOk or self.verbose > 0 and pdu.crcOk or self.verbose > 1:
                print pdu
        elif len(data) > self.rx_chips_min and self.verbose > 2:
            print 'Decode error'
            if self.verbose > 1:
                print to_hex(vec, format=1)
                print to_hex(err, format=1)
        

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-f", "--file", type="string", default=None,
                      help="Process the specified file [default=%default]")
    parser.add_option("-c", "--capture", type="string", default=None,
                      help="Capture only to the given file [default=%default]")
    parser.add_option("-v", "--verbose", type="int", default=0,
                      help="Verbose output [default=%default]")
    parser.add_option("-e", "--freq_error", type="float", default=-0.0021875,
                      help="Frequency error [default=%default]")
    (options, args) = parser.parse_args()
    #tb = wmbus_rx('/home/user/git/mbus/mine/traces/foo3.frame.f32')
    tb = wmbus_rx(options.file, options.capture, options.verbose, options.freq_error)
    tb.run()
    #print gen_map()
    

    for i in range(100000):
        f = i**2
