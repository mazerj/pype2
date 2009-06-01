function b = isp2mfile(obj)
%function b = isp2mfile(obj)
%
%  Is argument a p2mLoad file (not compressed)?
%
%Mon Jun  1 13:27:54 2009 mazer 
if ischar(obj)
  b = regexp(obj, '.*p2m$');
else
  b = 0;
end
