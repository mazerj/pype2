function c = strsplit(s, delim)

ix = [];
a = 1;
x = {};
for n=1:length(s)
  q = find(s(n) == delim);
  if ~isempty(q)
    b = n-1;
    x{length(x)+1} = s(a:b);
    a = n+1;
  end
end
x{length(x)+1} = s(a:end);
c = {};
for n=1:length(x)
  if ~isempty(x{n})
    c{length(c)+1} = x{n};
  end
end
