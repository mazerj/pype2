function printxd(pf)

xd = pf.extradata;

for n=1:size(xd, 2)
  fprintf('extradata{%d}\n', n);
  disp(xd{n});
end
  