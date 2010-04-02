function val = p2mset(var, val)
%function val = p2mset(var, val)
%
% Persistent name-value storage pairs (aka dictionary). Pairs
% are persistently stored in a file (~/.p2mset), which means
% this is not a fast function. Use with caution in speed critical
% code!
%
% INPUT
%   p2mset               - print table of values
%   val = p2mset(var)    - lookup value ([] for undefined)
%   p2mset(var, val)     - set var to val (returns val)
%   p2mset(var, [])      - clear/delete var
%   p2mset('!clearall')  - clear all vars
%
% OUTPUT
%   val - value (if any) of the named var -- [] for undefined.
%
%Wed Mar 31 14:05:35 2010 mazer -- created

fname = [getenv('HOME') '/.p2mset'];
if exist(fname, 'file')
  load('-mat', fname);
else
  tab.vars = {};
  tab.vals = {};
end

if nargin == 0
  % display table
  disp({'NAME' 'VALUE'});
  disp([tab.vars' tab.vals']);
  return;
elseif nargin > 0 && strcmp(var, '!clearall')
  tab.vars = {};
  tab.vals = {};
  if exist(fname, 'file')
    delete(fname);
  end
  return;
end

% find entry if table, if var exists
n = strmatch(var, tab.vars);

if isempty(n)
  % new var, create entry, unless val is []
  if nargin == 1
    val = [];
    return;
  end
  n = length(tab.vars)+1;
  tab.vars{n} = var;
  tab.vals{n} = 'never-set';
end

if nargin==2
  if isempty(val)
    % delete var from table
    ix = 1:length(tab.vars);
    ix = find(ix ~= n);
    tab.vars =  tab.vars(ix);
    tab.vals =  tab.vals(ix);
    val = [];
  else
    tab.vals{n} = val;
  end
  save(fname, 'tab');
else
  val = tab.vals{n};
end
