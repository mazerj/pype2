function pf = p2m(pypefile)
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
%  OUTPUT
%    PF = moderately complicated data structure containing all the data.
%      PF.rec contains entry for each trial
%      PF.extradata contains the "extradata" info
%      PF.src name of file data originated from
%
%Sun Feb 16 17:38:17 2003 mazer 
%
%Sat Mar  1 16:05:27 2003 mazer 
%   Removed the matfile option -- p2m no longer knows about writing
%   the resulting structure to disk.  The calling function (usually
%   p2mBatch) is responsible.

if nargin == 0
  fprintf('VISIBLE FUNCTIONS\n');
  fprintf('-----------------\n');
  fprintf('banner.m -- add header to plot window\n');
  fprintf('p2m.m -- generate single p2m file\n');
  fprintf('p2mLoad.m -- load p2m or ical file\n');
  fprintf('p2mSave.m -- same p2m or ical file\n');
  fprintf('p2mBatch.m -- generate p2m files in a batch\n');
  fprintf('p2mGetPPD.m -- \n');
  fprintf('p2mGetEyetrace.m -- \n');
  fprintf('p2mGetEyetraceRaw.m -- \n');
  fprintf('p2mEyecal2.m -- compute ical structure from eyecal data`run\n');
  fprintf('p2mEyecalApply.m -- apply ical structure to single trial\n');
  fprintf('p2mEyeStats.m -- estimate best guess for saccade vel threshold\n');
  fprintf('p2mFindEvents.m -- \n');
  fprintf('p2mFindFixes.m -- \n');
  fprintf('p2mFindSaccades.m -- \n');
  fprintf('p2mPlotEye.m -- \n');
  fprintf('p2mShow.m -- interactive trial browser\n');
  fprintf('p2mSpotmap.m -- revcor spotmap analysis\n');
  fprintf('p2mSpotmapBatch.m -- \n');
  fprintf('p2mSpotmapPlot.m -- \n');
  
  fprintf('\n');
  fprintf('INTERNAL FUNCTIONS\n');
  fprintf('------------------\n');
  fprintf('p2m_dir.m -- internal ls function\n');
  fprintf('p2mExit.m -- generate exit code\n');
  fprintf('p2mFileInfo.m -- get task info from src-filename\n');
  fprintf('p2mEyecalUnapply.m -- \n');
  fprintf('p2m_fitline.m -- \n');
  fprintf('p2m_fname.m -- \n');
  fprintf('p2m_abline.m -- plot regression line given slope & intercept\n');
  fprintf('p2m_getpid.m -- \n');
  fprintf('p2m_lreg.m -- \n');
  fprintf('bound.m -- find the boundaries on an ical\n');
  fprintf('cannonicalfname.m -- expand ~ etc to generate full pathname\n');
  fprintf('findcontour.m -- get (x,y) points for one contour\n');
  fprintf('getopts.m -- option parser; converts args to structure\n');
  
  fprintf('\n');
  fprintf('OBSOLETE FUNCTIONS\n');
  fprintf('------------------\n');
  fprintf('p2mEyecal.m -- old version of p2mEyecal2()\n');
  
  return
end

f = tempname;

cmd = sprintf('pype_expander %s %s >/dev/null', pypefile, f);
status = unix(cmd);
if status ~= 0
  error('Can''t find pype_expander or datafile, check path');
  return
end

origdir = pwd;
try
  cd(tempdir)
  fs = dir(sprintf('%s_*.m', f));
  for n=1:length(fs)
    f = fs(n).name(1:end-2);
    eval(f);
    delete(fs(n).name);
    %%%fprintf('Loaded record/extradata %d/%d\n', n, length(fs));
    rec(n).ttl_times = rec(n).spike_times;
    fprintf('.');
  end
  fprintf('\n');
  cd(origdir);
catch
  cd(origdir);
end


if ~exist('extradata', 'var')
  extradata = [];
end

pf.rec = rec;
pf.extradata = extradata;
pf.src = cannonicalfname(pypefile);

