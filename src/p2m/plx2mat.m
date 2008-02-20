function xd = plx2mat(fname, spikes, lfps, autosave)
%function xd = plx2mat(fname, spikes, lfps, autosave)
%
% Use plx2asc.py to convert and load the spike and LFP data from a .plx
% file into a compact, generic data stucture and optionally save it
% as a .mat file
%
% Note that the data structure returned is intended to abstract out
% the spike time, spike waveform (aka snippet) and slow lfp signals
% in a way compatible with both the plexon, TDT and anything else
% you might want to use... so eventually there sould be a tdt2mat etc..
%
% INPUT
%   fname -- name of .plx datafile (wildcard ok here, it will iterate)
%   spikes -- flag for spike extraction
%   lfps -- flag for lfp extraction
%   autosave -- optional flag (default=no) to save the result as a .mat
%               file; save file will be 'fname.mat' (in same dir)
%
% OUTPUT
%   matlab data structure 'xd'
%
%     xd.nunits -- vector of number of sorted units on each dsp channel
%     xd.haslfp -- vector of 0/1s indicating if lfps were recorded on this
%                   dps channel.
%         NOTE: both of these fields reflect the data in the original
%          .plx file, not the data loaded -- so if you choose not to load
%          lfp data (arg lfps==0), but the .plx file had lfp data, haslfp
%          fill indicate lfp's are present in the data!
%
%     xd.spk_chans{1..ntrials} -- spike channel/electrode number (1-based)
%     xd.spk_units{1..ntrials} -- unit number (0=unsorted)
%     xd.spk_times{1..ntrials} -- spike time (ms)
%
%     xd.lfp_chans{1..ntrials} -- spike channel/electrode number (1-based)
%     xd.lfp_times{1..ntrials} -- spike time (ms)
%     xd.lfp_volts{1..ntrials} -- unit number (0=unsorted)
%
%     xd.spw -- raw spike waveform data
%       xd.spw.trial -- trial number
%       xd.spw.channel -- electrode number (1-based)
%       xd.spw.unit -- unit number (0-based)
%       xd.spw.index -- time index relative to snippet start
%       xd.spw.time -- time in ms synced to pype
%       xd.spw.voltage -- voltages in mv
%
%     xd.spikes_flag -- spike data loaded?
%     xd.lfps_flag -- lfp data loaded?
%
% SEE ALSO
%   plx2asc.py, xdacq_spk, xdacq_lfp, xdacq_spw
%
%Tue Jan  8 09:53:18 2008 mazer

if nargin < 4
  autosave = 0;
end

flist = jls(fname);
if length(flist) > 1
  for n=1:length(flist)
    fprintf('%d/%d: %s\n', n, length(flist), flist{n});
    try
      if ~exist([flist{n} '.mat'], 'file')
	plx2mat(flist{n}, spikes, lfps, 1);
      else
	fprintf('.... skipped, .mat file alread exists\n');
      end
    catch
      e = lasterror;
      fprintf('WARNING: converting %s\n', flist{n});
      fprintf('         generated this error --\n', flist{n});
      disp(e.message);
    end
  end
  return
end

prefix = tempname();

cmd = sprintf('plx2asc.py -p %s %s', prefix, fname);
if spikes
  cmd = [cmd ' -s'];
end
if lfps
  cmd = [cmd ' -l'];
end
[status, result] = unix(cmd);
if status > 0
  error(result);
end
disp(result);

hdr = load([prefix '.hdr'], '-ascii');
delete([prefix '.hdr']);

spk = load([prefix '.spk'], '-ascii');
delete([prefix '.spk']);

lfp = load([prefix '.lfp'], '-ascii');
delete([prefix '.lfp']);

swaves = load([prefix '.spw'], '-ascii');
delete([prefix '.spw']);

if isempty(lfp)
  nl = 0;
else
  nl = max(lfp(:,1));
end
if isempty(spk)
  ns = 0;
else
  ns = max(spk(:,1));
end
ntrials = max(nl, ns);
if ntrials == 0
  error('no spike or lfp data loaded');
end

xd.nunits = hdr(:,2);
xd.nsortedunits = zeros(size(hdr(:,2)));
xd.haslfp = hdr(:,3);

if ~isempty(spk)
  for i = 1:length(xd.nunits)
    %
    % fix nunits by actually scanning the data for any detected
    % spikes on the specified channel.. not sure why this is necessary,
    % but apparently sometimes nunits can be non-zero even when there
    % are no spikes on the channel
    %
    % this will set nunits to 1 if there are any sorted or unsorted
    % spike events on the indicated channel -- then we can just ignore
    % the plexon nunits field and use this. Note that unsorted units
    % count as units here! If you want only sorted units, look at
    % xd.nsortedunits instead..
    %
    units = unique(spk(spk(:,2) == i, 3));
    xd.nunits(i) = length(units);
    xd.nsortedunits(i) = sum(units > 0);
  end
end
  
xd.spk_chans = {};
xd.spk_units = {};
xd.spk_times = {};
  
xd.lfp_chans = {};
xd.lfp_volts = {};

for n=1:ntrials
  if ~isempty(spk)
    ix = find(spk(:,1) == n);
    xd.spk_chans{n} = spk(ix, 2);
    xd.spk_units{n} = spk(ix, 3);
    xd.spk_times{n} = spk(ix, 4);
  else
    xd.spk_chans{n} = [];
    xd.spk_units{n} = [];
    xd.spk_times{n} = [];
  end

  if ~isempty(lfp)
    ix = find(lfp(:,1) == n);
    xd.lfp_chans{n} = lfp(ix, 2);
    xd.lfp_times{n} = lfp(ix, 3);
    xd.lfp_volts{n} = lfp(ix, 4);
  else
    xd.lfp_chans{n} = [];
    xd.lfp_times{n} = [];
    xd.lfp_volts{n} = [];
  end
end

if ~isempty(swaves)
  xd.spw.trial = swaves(:,1);
  xd.spw.channel = swaves(:,2);
  xd.spw.unit = swaves(:,3);
  xd.spw.index = swaves(:,4);
  xd.spw.time = swaves(:,5);
  xd.spw.volt = swaves(:,6);
else
  xd.spw.trial = [];
  xd.spw.channel = [];
  xd.spw.unit = [];
  xd.spw.index = [];
  xd.spw.time = [];
  xd.spw.volt = [];
end

% save arguments so we know what got loaded..
xd.spikes_flag = spikes;
xd.lfps_flag = lfps;

if autosave
  fout = [fname '.mat'];
  save(fout, 'xd', '-mat');
  fprintf('Saved to %s\n', fout);
end
