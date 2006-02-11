function pf = p2mSelect(pf, channel, unit)
%function pf = p2mSelect(pf, channel, unit)
%
% Extract PlexNet spikes from channel/unit and stick them in spike_times
% so existing software can use the data unchanged.
%
% INPUT
%   pf = p2m data strcture
%   channel = electrode # (1-N)  --> specify -1 for TTL datastream
%   unit = sorted unit number (1-N)
%
% OUTPUT
%   pf = modified pf data structure with the new spike times in place
%
%Sun Dec  4 21:10:28 2005 mazer 

if nargin == 1
  l = [];
  for n = 1:length(pf.rec)
    for k = 1:length(pf.rec(n).plx_times)
      l = [l; pf.rec(n).plx_channels(k) pf.rec(n).plx_units(k)];
    end
  end
  l = unique(l, 'rows');
  for k = 1:size(l, 1)
    fprintf('chn %03d, unit %d\n', l(k,1), l(k,2));
  end
else
  for n = 1:length(pf.rec)
    if channel >= 0
      ts = [];
      for k = 1:length(pf.rec(n).plx_times)
	if pf.rec(n).plx_channels(k) == channel && ...
	      pf.rec(n).plx_units(k) == unit
	  ts = [ts pf.rec(n).plx_times(k)];
	end
      end
      pf.rec(n).spike_times = ts;
    else
      pf.rec(n).spike_times = pf.rec(n).ttl_times;
    end
  end
end
  
