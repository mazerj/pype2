function [p, pval] = f2g(varargin)

if strcmp(varargin{1}, 'fit') == 1
  x = varargin{2};
  y = varargin{3};
  if length(varargin) > 3
    v = varargin{4};
    if ~isempty(v)
      v(v == 0) = 1e-20;
    end
  else
    v = [];
  end
  
  % guess at initial params:
  mu1 = min(x) + 0.05 * (max(x)-min(x));
  mu2 = min(x) + 0.95 * (max(x)-min(x));
  
  dx = abs(mean(diff(sort(x))));
  sigma1 = 4.0 * dx;
  sigma2 = 3.0 * dx;
  
  gain1 = max(y)-min(y);
  gain2 = 0.5 * gain1;
  
  offset = min(y);
  
  p0 = [mu1 sigma1 gain1 mu2 sigma2 gain2 offset];

  opts = optimset(optimset('fminsearch'), 'Display', 'off');
  [p, fval, exitflag, output] = fminsearch('f2g', ...
					   p0, opts, x, y, v);

  if exitflag < 0
    fprintf(1, 'warning: exitflag ~= 1; poor convergence.\n');
  end
  
  if nargout == 2
    yhat = f(p, x);
    n = min(length(x).^2, 100);
    pval = goodfit(x, yhat, n);
  end
elseif strcmp(varargin{1}, 'plot') == 1
  x0 = varargin{2};
  p = varargin{3};
  if length(varargin) > 3
    l = varargin{4};
  else
    l = '-';
  end
  
  x = min(x0):(max(x0)-min(x0))/100:max(x0);
  yhat = f(p, x);
  l = plot(x, yhat, l);
  if length(varargin) > 4
    hold on;
    plot(x0, varargin{5}, 'o');
    hold off;
  end
  p = l;
else
  p = objective(varargin{:});
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function y = f(p, x)
mu1 = p(1);
sigma1 = p(2);
gain1 = p(3);
mu2 = p(4);
sigma2 = p(5);
gain2 = p(6);
offset = p(7);

y = offset + ...
    (gain1 .* exp(-((x - mu1).^2) ./ (2 .* (sigma1.^2)))) + ...
    (gain2 .* exp(-((x - mu2).^2) ./ (2 .* (sigma2.^2))));


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function e = objective(p, x, y, v)

mu1 = p(1);
sigma1 = p(2);
gain1 = p(3);
mu2 = p(4);
sigma2 = p(5);
gain2 = p(6);
offset = p(7);

if sigma1 <= 0 | sigma2 <= 0 | gain1 <= 0 | gain2 <= 0 | ...
      mu1 < min(x) | mu1 > max(x) | mu2 < min(x) | mu2 > max(x)
  e = +Inf;
  return
end

yhat = f(p, x);

if isempty(v)
  % w/o variance just minimize least sq error
  e = mean((yhat - y) .^ 2);
else
  % w/o variance otherwise, try to minimize chi2 error
  e = sum(((yhat - y).^2) ./ v);
end

if 0
  figure(2);
  clf
  plot(x, y, 'bo', x, yhat, 'r-');
  drawnow;
  p
end
