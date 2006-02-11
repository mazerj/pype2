function p2mpp(pf, recno)
%function p2mpp(pf, recno)
%
% pretty print trial data
%
%Tue Nov 22 15:05:07 2005 mazer 

pf=p2mLoad(pf);

nrec = length(pf.rec);
if ~exist('recno', 'var')
  recno = 1;
end

if recno < 1 | recno > nrec
  error('out of bounds');
end

for n = 1:length(pf.rec(recno).ev_e)
  fprintf('%6d ms\t<%s>\n', pf.rec(recno).ev_t(n), pf.rec(recno).ev_e{n})
end
