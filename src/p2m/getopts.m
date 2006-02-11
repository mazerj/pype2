function defaults = getopts(defaults, varargin)
%function defaults = getopts(defaults, varargin)
%
%  Build a structure from optional/variable argument list.  Input
%  is a structure of default values.  Fields are added or modified
%  in the default structure according to the vararin values:
%    s.foo = 1;
%    s.baz = 2;
%    s = getopts(defaults, 'foo', 10, 'baz', -1)
%    s = 
%        foo: 10
%        baz: -1
%
%  And so on.  This is most useful in the following way:
%    function f(x, y, z, varargin}
%    opts.a = 1;
%    opts.b = 2;
%    opts = getops(opts, varargin{:});
%    ....
%
%
%Tue Mar  4 15:19:19 2003 mazer 

for n = 1:2:length(varargin)
  defaults = setfield(defaults, varargin{n}, varargin{n+1});
end
