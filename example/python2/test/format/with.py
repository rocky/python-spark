if sys.argv[i] == '--scan':
    do_scan_only = True
    scan = Python2Scanner()
    do_format = False
    i += 1
for path in sys.argv[i:]:
    if os.path.exists(path):
        continue
with open(path, 'r') as fp:
    pass
