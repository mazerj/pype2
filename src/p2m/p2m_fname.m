function fname = p2m_fname(fname)

% expand DATAROOT
if ~isempty(findstr(fname, '+')) & ~isempty(getenv('DATAROOT'))
  fname = strrep(fname, '+', getenv('DATAROOT'));
end

% expand HOME
if ~isempty(findstr(fname, '~')) & ~isempty(getenv('HOME'))
  fname = strrep(fname, '~', getenv('HOME'));
end
