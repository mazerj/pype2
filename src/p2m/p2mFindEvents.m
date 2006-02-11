function [ix, ts] = p2mFindEvents(pf, n, evname)
%function [ix, ts] = p2mFindEvents(pf, n, evname)
%
% Find events prefix-matching 'evname' in the nth record of pf.
%
% INPUT
%   pf = p2m data strcture
%   n = record number
%   evname = string to search for in event table
%
% OUTPUT
%   ix = indices of matching events in pf.rec(n).ev_e/ev_t
%   ts = times (in ms!) of matching events.
%
%Thu Mar 27 22:18:31 2003 mazer 

pf=p2mLoad(pf);

ix = strmatch(evname, pf.rec(n).ev_e);
ts = pf.rec(n).ev_t(ix);
