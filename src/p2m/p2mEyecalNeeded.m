function tf = p2mEyecalNeeded(pf, n)

tf = ~isfield(pf.rec(n), 'raweyex');
