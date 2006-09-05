function p2mpp(pf, recno)
%function p2mpp(pf, recno)
%
% pretty print trial data -- prints list of events, parameter
% dictionaries (param and userparam) and result code etc.
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


fprintf('--EVENTS---------------------------------------\n');

for n = 1:length(pf.rec(recno).ev_e)
  fprintf('%6d ms\t<%s>\n', pf.rec(recno).ev_t(n), pf.rec(recno).ev_e{n})
end

fprintf('--USERPARAMS-----------------------------------\n');

plist = fields(pf.rec(recno).userparams);
for n = 1:length(plist)
  fprintf('%20s ', plist{n});
  v = getfield(pf.rec(recno).userparams, plist{n});
  try
    fprintf('%s\n', num2str(v));
  catch
    disp(getfield(pf.rec(recno).userparams, plist{n}));
  end
end

fprintf('--PARAMS---------------------------------------\n');

plist = fields(pf.rec(recno).params);
for n = 1:length(plist)
  fprintf('%20s ', plist{n});
  v = getfield(pf.rec(recno).params, plist{n});
  try
    fprintf('%s\n', num2str(v));
  catch
    disp(getfield(pf.rec(recno).params, plist{n}));
  end
end

fprintf('--HEADER-CODES---------------------------------\n');

fprintf('result=%s\n', pf.rec(recno).result);

fprintf('-----------------------------------------------\n');
