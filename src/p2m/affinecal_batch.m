function affinecal_batch(files)

bad = [];
for n = 1:length(files)
  out = strrep(strrep([files{n} '.aff'], '.gz', ''), '.p2m', '');
  fprintf(' in: %s\nout: %s\n', files{n}, out);
  pf = p2mLoad(files{n});
  try
    clf;
    affinecal(pf, out);
    drawnow;
  catch
    unix(sprintf('/bin/rm -f %s %s.ps', out, out));
    bad = [bad n];
  end
end

if length(bad) > 0
  fprintf('---------- failures -------------\n');
  for n=1:length(bad)
    fprintf('failed: %s\n', files{n});
  end
end

