import os, sys
i = 0
if sys.argv[i] == '--scan':
    scan = os.path.join('a', 'b')


for path in sys.argv[i:]:
    if os.path.exists(path):
        continue
with open(path, 'r') as fp:
    pass
