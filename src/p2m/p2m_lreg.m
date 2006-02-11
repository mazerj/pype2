function [a, b] = p2m_lreg(x, y, style1, style2)
%function [a, b] = p2m_lreg(x, y, style1, style2)

% get rid of any nan's first..
ix = ~isnan(x) & ~isnan(y);
x=x(ix);
y=y(ix);

[a, b] = p2m_fitline(x, y);
xe = [min(x) max(x)];
ye = (a * xe) + b;

if ~exist('style1')
  style1='ko';
end

if ~exist('style2')
  style2='r-';
end

if length(style1) > 0
  plot(x, y, style1);
end

if length(style2) > 0
  hold on;
  plot(xe, ye, style2);
  hold off;
end
