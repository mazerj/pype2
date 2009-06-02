function pf=p2mNoFalseSpikes(pf)
%function pf=p2mNoFalseSpikes(pf)
%
%  - Look for TTL spikes in a newly loaded datafile that occur right
%    after ADC starts and strip them out
%  - This is needed because pype's TTL-detection algorithm sometimes
%    gets confused and detects the onset of ADC as a spike. So the
%    first spike usually has a timestamp exactly equal to the onset
%    of ADC ('eye_start'). To be safe, this considers anyting within
%    +-5ms of the 'eye_start' signal gabarge.
%  - this should be called immediately after loading by p2mLoad(). Users
%    should never have to deal with this function directly
%
% Tue Jun  2 10:14:10 2009 mazer 

k=0;
for n=1:length(pf.rec)
  [ix, ts] = p2mFindEvents(pf,n,'eye_start');
  if length(ts) & abs(pf.rec(n).spike_times(1) - ts(1)) < 5
    % false spike detection
    pf.rec(n).spike_times = pf.rec(n).spike_times(2:end);
    pf.rec(n).ttl_times = pf.rec(n).ttl_times(2:end);
    k = k + 1;
  end
end
if k > 0
  fprintf('warning: removed %d false initial spikes\n', k);
end

