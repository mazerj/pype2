function result = p2m_dir(pat)
% this is jls() from jamie's toolbox -- matlab's dir() function
% is fucked -- this one returns a list of filenames without loosing
% the directory names..


[ecode, x] = unix(sprintf('/bin/ls -1 %s', pat));
result = {};
if ecode == 0
  nl = find(x == 10);
  a = 1;
  n = 1;
  for ix=1:length(nl)
    b = nl(ix)-1;
    result{n} = x(a:b);
    a = b + 2;
    n = n + 1;
  end
end

