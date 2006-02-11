
load kmeans.mat


data = [cx; cy]';

a1 = min(data(:,1));
a2 = max(data(:,1));
b1 = min(data(:,2));
b2 = max(data(:,2));
ctrs = rand(10,2);
ctrs(:,1) = (ctrs(:,1) * (a2-a1)) + a1;
ctrs(:,2) = (ctrs(:,2) * (b2-b1)) + b1;
ctrs(1,1) = 0;
ctrs(1,2) = 0;



options = foptions;
options(1)  = 0;
options(2) = 0.1;
options(14) = 1000;
[ctrs, opts, post] = kmeans(ctrs, data, options);


c='mcrgbmcrgbmcrgbmcrgbwmcr';
s='ox+*sdv><ph.ox+ox+*sdv><';

v = jet(n);
ix = randperm(size(v, 1));
v = v(ix,:);

leg = {};
for n=1:size(post,2)
  ix=find(post(:,n) == 1);
  %plot(data(ix,1), data(ix,2), [c(n) s(n)]);
  l = plot(data(ix,1), data(ix,2), s(n));
  set(l, 'markerfacecolor', v(n,:), 'color', v(n,:));
  hold on;
  leg{n} = num2str(n);
end
hold off;
set(gca, 'color', 'none');
legend(leg);

