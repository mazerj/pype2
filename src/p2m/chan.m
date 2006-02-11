function s = chan(s)

if nargin == 1
  unix(['pypespike ' s]);
else
  [xxx, s] =  unix('pypespike -query');
end
