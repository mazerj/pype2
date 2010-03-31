function val = p2mset(var, val)
%
% persistent name-value storage pairs (for fixed parameters)
%
%Wed Mar 31 14:05:35 2010 mazer -- created

persistent ptab

if isempty(ptab)
  ptab.vars = {};
  ptab.vals = {};
end

if nargin == 0
  for n = 1:length(ptab.vars)
    fprintf('%s=%s\n', ptab.vars{n},  ptab.vals{n});
  end
  val = [];
  return
end

n = strmatch(var, ptab.vars);
if isempty(n)
  if nargin == 1
    val = [];
    return;
  end
  n = length(ptab.vars)+1;
  ptab.vars{n} = var;
end

if nargin==2
  ptab.vals{n} = val;
end
val = ptab.vals{n};
