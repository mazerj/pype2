function [x,y]=findcontour(x, y, z, level)

c = contourc(x, y, z, [level level]);
[x, y] = c2xy(c);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [x, y] = c2xy(c)
x=[];
y=[];
n = 1;
while n < size(c, 2)
  a = n+1;
  b = a+c(2,n)-1;
  x = [x c(1, a:b)];
  y = [y c(2, a:b)];
  n = b+1;
end
x=x';
y=y';

