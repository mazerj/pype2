function foo(pf)
%function p2mSpotmap(pf)
%
%  Compute spotmap kernel from p2m file.
%
%  INPUT
%    pf = p2m datastructure
%
%  OUTPUT
%    S = ???
%
%Sun Feb 23 09:24:09 2003 mazer 

ppd = p2mGetPPD(pf, 1);
nrec = length(pf.rec);
binwidth = 2*16;
start = 0;
stop = 250;
smooth = 1.0;

S = [];
for recno=1:nrec
  [ix_on,ts_on]=p2mFindEvents(pf, recno, 'spot on');
  for n=1:length(ix_on)
    k = 1+size(S,1);
    ev = strsplit(pf.rec(recno).ev_e{ix_on(n)}, ' ');
    S(k, 1) = str2num(ev{3});
    S(k, 2) = str2num(ev{4});
    S(k, 3) = str2num(ev{5});
  end
end
S = unique(S, 'rows');

T = start:1:stop;
K = zeros([size(S, 1) size(T,2)]);
Kn = zeros([size(S, 1) size(T,2)]);

for recno=1:nrec
  [ix_on,ts_on]=p2mFindEvents(pf, recno, 'spot on');
  [ix_off,ts_off]=p2mFindEvents(pf, recno, 'spot off');

  for n=1:length(ix_off)
    ev = strsplit(pf.rec(recno).ev_e{ix_on(n)}, ' ');
    x = str2num(ev{3});
    y = str2num(ev{4});
    p = str2num(ev{5});
    row = find(S(:,1)==x & S(:,2)==y & S(:,3)==p);
    
    for k=1:length(pf.rec(recno).spike_times)
      % spike time relative to spot onset
      st = pf.rec(recno).spike_times(k) - ts_on(n);
      v = (T==st);
      K(row, v) = K(row, v) + 1;
    end
    Kn(row, :) = Kn(row, :) + 1;
  end
end
Kn(Kn == 0) = NaN;
K = K ./ Kn;

t = sort([(-binwidth:-binwidth:start) 0:binwidth:stop]);
k = zeros([size(S, 1) size(t,2)-1]);
for n=2:size(t,2)
  ix = find(T >= t(n-1) & T < t(n));
  k(:, n-1) = 1000.* mean(K(:,ix),2) / length(ix);
end

xg = unique(S(:,1));
yg = unique(S(:,2));
pg = unique(S(:,3));


Z = NaN.*zeros([size(yg,1) size(xg,1) size(pg,1) size(t, 2)-1]);
for pn = 1:length(pg)
  for xn = 1:length(xg)
    for yn = 1:length(yg)
      row = find(S(:,1)==xg(xn) & S(:,2)==yg(yn) & S(:,3)==pg(pn));
      if ~isempty(row)
	Z(yn, xn, pn, :) = k(row, :);
      end
    end
  end
end

vmax = -1;
for k = 1:size(Z,4)
  slice = Z(:,:,:,k);
  v = var(slice(:));
  if v > vmax
    vmax = v;
    vmaxslice = k;
  end
end

clf
n = size(t,2)-1;
ncol = n+1;
nrow = 5;
for k = 1:n
  subplot(nrow, ncol, k+(ncol*0));
  kp(yg, xg, 1*Z(:,:,1,k) + 0*Z(:,:,2,k), smooth, ppd);
  set(gca, 'ydir', 'normal');
  axis image;
  ylabel('off');
  if k > 1
    axis off;
  end
  if k == vmaxslice
    title(sprintf('* %dms', t(k)));
  else
    title(sprintf('%dms', t(k)));
  end
  
  subplot(nrow, ncol, k+(ncol*1));
  kp(yg, xg, 0*Z(:,:,1,k) + 1*Z(:,:,2,k), smooth, ppd);
  set(gca, 'ydir', 'normal');
  axis image;
  ylabel('on');
  if k > 1
    axis off;
  end

  subplot(nrow, ncol, k+(ncol*2));
  kp(yg, xg, 0.5*Z(:,:,1,k) + 0.5*Z(:,:,2,k), smooth, ppd);
  set(gca, 'ydir', 'normal');
  axis image;
  ylabel('on+off');
  if k > 1
    axis off;
  end

  subplot(nrow, ncol, k+(ncol*3));
  kp(yg, xg, 1*Z(:,:,1,k) + -1*Z(:,:,2,k), smooth, ppd);
  set(gca, 'ydir', 'normal');
  axis image;
  ylabel('on-off');
  if k > 1
    axis off;
  end
end

c = [];
for k = 1:(nrow-1)
  for n = 1:(ncol-1)
    subplot(nrow, ncol, (k-1) * ncol + n)
    c = [c; caxis];
  end
end

for k = 1:(nrow-1)
  for n = 1:(ncol-1)
    subplot(nrow, ncol, (k-1) * ncol + n)
    caxis(max(c));
  end
end

subplot(nrow, 2, (2*nrow)-1);
y = 1000 * mean(K);
y = smooth1d(y, 5, 16);
plot(T, y);
axis tight;
ylabel('hz');
xlabel('ms');
vline(0*pf.rec(1).params.spot_dur);
vline(1*pf.rec(1).params.spot_dur);
vline(2*pf.rec(1).params.spot_dur);
fprintf('\n');

subplot(nrow, 2, (2*nrow));
text(0, 0.5, ...
     {pf.src ...
      sprintf('binwidth=%dms', binwidth) ...
      sprintf('smooth=%.1f', smooth)});
axis off
box off;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5

function kp(yg, xg, k, smooth, ppd)

%imagesc(yg, xg, k);
if smooth > 0
  k = smooth2d(k, 2, 2, smooth, 0);
end
contourf(xg/ppd, yg/ppd, k);
fprintf('.');
colormap(hotcold(1));

