function p2mBatch(wildcard, inplace, exitOnError)
%function p2mBatch(wildcard, inplace, exitOnError)
%
%  Batch engine for converting pype files into matlab loadable
%  datafiles.  Given a wildcard pattern of pype file names, this
%  does through them and automatically generates *.p2m files
%  for each datafile and saves to XXX.p2m
%
%  INPUT
%    wildcard = CSH-style wildcard pattern of files to crunch
%    inplace = Boolean (0/1) specifying where to put p2m files.
%		If true, then matlab (.p2m) files will be
%		written into the same directory the original
%		datafiles came from.
%
%  OUPUT
%    none -- just writes the datafiles to disk.
%
%Sun Feb 16 17:36:37 2003 mazer 
%
% Revisions
%
% Wed May 28 11:49:01 2003 mazer 
%   - added code to exclude .p2m files for BW
%   - also runs to the end, reporting errors at the very
%     end in a table
% 

if ~exist('inplace', 'var')
  inplace = 0;
end

if ~exist('exitOnError', 'var')
  exitOnError = 0;
end

% get list of files to process, excluding .p2m files
xxx = p2m_dir(wildcard);
files = {};
k = 1;
for n = 1:length(xxx)
  if strcmp(xxx{n}((end-3):end),'.p2m') == 0
    files{k} = xxx{n};
    k = k + 1;
  end
end
if length(files) == 0
  fprintf(2, 'Nothing to convert, stopping.\n');
  return
end
  

errors = {};

for n = 1:length(files)
  pypefile = char(files(n));
  
  if inplace
    matfile = [pypefile '.p2m'];
  else
    ix = find(pypefile == '/');
    if length(ix) > 0
      matfile = pypefile((ix(end)+1):end);
    else
      matfile = pypefile;
    end
    matfile = ['./' matfile '.p2m'];
  end
  matfile = strrep(matfile, '.gz', '');
  
  if p2mExist(matfile)
    oldpf = p2mLoad(matfile);
  else
    oldpf = [];
  end

  try
    PF = p2m(pypefile, oldpf);
    save(matfile, 'PF', '-mat');
    errors{n} = '';
  catch
    fprintf(2, 'Error converting file: %s\n', pypefile);
    if exitOnError
      p2mExit(1);
    else
      errors{n} = lasterr;
    end
  end
end

waserr = 0;
for n = 1:length(files)
  pypefile = char(files(n));
  if length(errors{n}) ~= 0
    fprintf(2, '----------------------------------------------------\n');
    fprintf(2, '%s: error\n%s\n', pypefile, errors{n});
    fprintf(2, '----------------------------------------------------\n');
  end
end
