function plot_dmod(sstart,slen,ofs)

if nargin < 3
  ofs=0
endif

d1 = read_float_binary('fmdemod.dat');
d2 = read_float_binary('clock_recovery.dat');
d3 = read_char_binary('slicer.dat') -.5;
%plot([1:12772],d1, [1:16:797*16],d2)
%toggle_plplot_use 

mlen = min([floor(length(d1)/16) length(d2) length(d3)]);
slen = min(slen, mlen-sstart);
d2f = reshape(repmat(d2,1,16)',1,16*length(d2));
d3f = reshape(repmat(d3,1,16)',1,16*length(d3));

idx = [1:slen*16];
idx = idx + 16*sstart;
scale = 16;%1.6e3;
%plot(idx/scale,d1(idx), idx/scale,d2f(idx), idx/scale,d3f(idx));
plot(idx/scale,d1(idx), (idx-ofs)/scale,d2f(idx), (idx-ofs)/scale,d3f(idx));
%plot(idx/scale,d2f(idx));
grid on
xlim([min(idx/scale) max(idx/scale)])