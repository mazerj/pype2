function r = p2mLoad(fname, plexchan, verbose)
%function r = p2mLoad(fname, plexchan, verbose)
%
%  Loads '.p2m' and '.ical' files generated by the p2m
%  tools. File suffix is used to figure out what kind of
%  file it is..
%
%  This is really just a wrapper for the built in LOAD
%  function which only recognized the '.mat' extension.
%
%  INPUT
%    fname = ascii filename
%    plexchan = OPTIONAL plexon channel to select on load (format: "005a" etc)
%      (this call p2mSelect, replacing the spike_times list with the
%       indicated channel). For TTL data, don't specify this argument, or
%       use 'TTL'.
%    verbose = print info as you go... default verbose=1
%
%  OUTPUT
%    t = data structure generated by p2m tools:
%            p2m/p2mBatch/p2mEyecalBatch etc..
%
%Mon Feb 17 16:19:31 2003 mazer 
%
%Tue Apr 15 19:09:30 2003 mazer 
%  Modified to automatically handle .gz files.
%  Along those lines -- if the specified file doesn't
%   exist, it will automatically append a '.gz' and
%   try for that.
%
%Wed May 28 12:12:40 2003 mazer 
%  Modified to return right away if a pf datastruct
%  is passed in instead of a filename
%
%Fri Oct 27 12:38:39 2006 mazer 
%  added plexchan option
%
%Fri Aug  8 12:42:05 2008 mazer 
%  added verbose option
%
%Tue Jun  2 10:17:23 2009 mazer 
%  added automatic call to p2mNoFalseSpikes
%
%Tue Oct 12 10:25:17 2010 mazer 
%  Added automatic downsampling for new oversampled timebase.
%  comedi_server now samples >1khz and saves timestamps is
%  microsecs instead of millisecs. p2mLoad() now uses interp1
%  to downsample to a fixed 1khz base when oversampling is
%  detected.
%
%  Also, added a warning when duplicated timestamps are
%  detected in eyet!

if ~exist('verbose', 'var'), verbose = 1; end

if ~ischar(fname)
  % if it's not a char, then assume it's an already loaded
  % pf structure and just return it..
  r = fname;
  if exist('plexchan', 'var') && ~isempty(plexchan)
    r = p2mSelect(r, plexchan);
  end
  return
end

% expand wildcard, if any..
flist = p2m_dir(fname);
if length(flist) > 0
  fname = flist{1};
end

if strcmp(fname((end-2):end), '.gz') == 1
  gz = 1;
  fname = fname(1:(end-3));
else
  gz = 0;
end

fname2 = p2m_fname(fname);

if ~p2mExist(fname2) & p2mExist([fname2 '.gz'])
  gz = 1;
end
  
if ~strcmp(fname2, fname)
  fname = fname2;
  if verbose
    fprintf('true file: %s\n', fname);
  end
end
if gz
  if verbose
    fprintf('gzip: automatic\n');
  end
end

fname0 = fname;
fname = cannonicalfname(fname);
if strcmp(fname0, fname) == 0
  % only print warning if cannonical name doesn't match the
  % name specified by user
  if verbose
    fprintf('loading: %s\n', fname);
  end
end

if fname(end-3:end) == '.p2m'
  if gz
    gzload([fname '.gz']);
  else
    load(fname, '-mat');
  end
  if verbose
    fprintf('%d trials\n', length(PF.rec));
  end
  % strip false spikes from PF right away! these are spikes
  % generated at the onset of ADC by the crappy TTL detection
  % algorithm pype uses... see p2mNoFalseSpikes() doc
  r = p2mNoFalseSpikes(PF, verbose);
elseif fname(end-4:end) == '.ical'
  if gz
    gzload([fname '.gz']);
  else
    load(fname, '-mat');
  end
  r = ical;
elseif fname(end-3:end) == '.fix'
  if gz
    gzload([fname '.gz']);
  else
    load(fname'-mat');
  end
  r = fixes;
else
  error(['unknown file type: ' fname]);
end

if exist('plexchan', 'var') && ~isempty(plexchan)
  r = p2mSelect(r, plexchan);
end

% check for duplicate eyet values:
dups = 0;
for n = 1:length(r.rec)
  if length(unique(r.rec(n).eyet)) ~= length(r.rec(n).eyet)
    fprintf('warning: file contains dup eyet values (rec=%d)\n', n);
    dups = 1;
    break
  end
end

% check for oversampling (eyet > 1khz; no duplicates) 
% and downsample to 1khz (1ms sampling interval).
if ~dups
  % w/matlab7 NaN's are not allowed in Y for interp1:
  %% warning('off');
  for n = 1:length(r.rec)
    if min(diff(r.rec(n).eyet)) < 1
      r.rec(n).oeyet = r.rec(n).eyet;
      r.rec(n).orealt = r.rec(n).realt;
      r.rec(n).oeyex = r.rec(n).eyex;
      r.rec(n).oeyey = r.rec(n).eyey;
      r.rec(n).oeyep = r.rec(n).eyep;
      r.rec(n).oraw_photo = r.rec(n).raw_photo;
      r.rec(n).oraw_spike = r.rec(n).raw_spike;
      
      r.rec(n).eyet = (round(r.rec(n).oeyet(1)):1:round(r.rec(n).oeyet(end)))';
      r.rec(n).realt = NaN;
      r.rec(n).eyex = interp1(r.rec(n).oeyet, r.rec(n).oeyex, ...
                               r.rec(n).eyet);
      r.rec(n).eyey = interp1(r.rec(n).oeyet, r.rec(n).oeyey, ...
                               r.rec(n).eyet);
      r.rec(n).eyep = interp1(r.rec(n).oeyet, r.rec(n).oeyep, ...
                               r.rec(n).eyet);
      r.rec(n).raw_photo = interp1(r.rec(n).oeyet, r.rec(n).oraw_photo, ...
                               r.rec(n).eyet);
      r.rec(n).raw_spike = interp1(r.rec(n).oeyet, r.rec(n).oraw_spike, ...
                               r.rec(n).eyet); 
    end
  end
  %%warning('on');
end
  
  


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5

function z = gzload(fname)

t = tempname;
[s, w] = unix(sprintf('gunzip <%s >%s', fname, t));
if s
  error(sprintf('can''t find %s', fname));
end
evalin('caller', sprintf('load(''%s'', ''-mat'')', t));
delete(t);
