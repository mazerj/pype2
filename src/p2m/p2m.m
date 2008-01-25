function pf = p2m(pypefile, oldpf)
%function pf = p2m(pypefile)
%
%  Convert and load a raw pype datafile into a matlab data
%  structure.  This requires the program pype_expander.py to
%  be on the user's path somwehere AND a fully installed
%  version of pypenv on the machine you're running on.
%
%  INPUT
%    pypefile = string containing name (full path) of original pype
%		data file.
%
%    oldpf = previously extracted PF structure or name of p2m file.
%            data in pypefile will be converted, extracted and tacked
%            on at the end of oldpf and returned as pf
%
%  OUTPUT
%    pf = moderately complicated data structure containing all the data.
%      pf.rec contains entry for each trial
%      pf.extradata contains the "extradata" info
%      pf.src name of file data originated from
%
% Sun Feb 16 17:38:17 2003 mazer 
%
% Sat Mar  1 16:05:27 2003 mazer 
%   Removed the matfile option -- p2m no longer knows about writing
%   the resulting structure to disk.  The calling function (usually
%   p2mBatch) is responsible.
%
% Sun May 21 13:58:44 2006 mazer 
%   added support to appending new data to existing p2m structure. If you
%   pass in an old data struct, only the new data will be converted and
%   appended to the existing data.
%  

if nargin == 0
  p2mHelp()
  return
end

if ~exist('oldpf', 'var')
  oldpf = [];
elseif ischar(oldpf)
  oldpf = p2mLoad(oldpf);
end

f = tempname;

if isempty(oldpf)
  n = 0;
else
  n = length(oldpf.rec);
end 

cmd = sprintf('pype_expander.py %s %s %d >/dev/null', pypefile, f, n);
status = unix(cmd);
if status ~= 0
  error('Can''t find pype_expander.py or datafile, check path');
  return
end

rec = [];
origdir = pwd;
try
  cd(tempdir)
  fs = dir(sprintf('%s_*.m', f));
  for n=1:length(fs)
    f = fs(n).name(1:end-2);
    try
      eval(f);
    catch
      err = lasterror;
      fprintf('\n');
      fprintf('ERROR converting record #%d from %s:\n', n, pypefile);
      fprintf('%s\n', err.message);
      fprintf('\n');
      rethrow(err);
    end
    delete(fs(n).name);
    rec(n).ttl_times = rec(n).spike_times;
    fprintf('.');
  end
  cd(origdir);
catch
  cd(origdir);
end
fprintf('\n');

if ~exist('extradata', 'var')
  extradata = [];
end


if isempty(oldpf)
  fprintf('Converted %d trials.\n', length(rec));
  pf.extradata = extradata;
  pf.src = cannonicalfname(pypefile);
  pf.rec = rec;
elseif isempty(rec)
  fprintf('No new data converted.\n');
  pf = oldpf;
else
  fprintf('Converted %d new trials.\n', length(rec) - length(oldpf.rec));
  pf.extradata = extradata;
  pf.src = cannonicalfname(pypefile);
  pf.rec = rec;
  % merge in the old data for return 
  if ~isempty(oldpf)
    for n = 1:length(oldpf.rec)
      pf.rec(n) = oldpf.rec(n);
    end
  end
end

