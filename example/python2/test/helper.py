import sys, os, difflib

def compare_one(func, python_file):
    right_file = python_file[:-2] + 'right'
    got_file = python_file[:-2] + 'got'
    with open(python_file, 'r') as py_fp:
        input_data = py_fp.read()
        tokens = func(input_data)
        got = [str(t)+"\n" for t in tokens]
        same = True
        with open(right_file, 'r') as right_fp:
            right_data = right_fp.readlines()
            lines = difflib.unified_diff(got, right_data,
                                         fromfile=right_file, tofile=got_file)
            for line in lines:
                same = False
                sys.stdout.write(line)
                pass
            pass
        if not same:
            # print("XXX ", python_file)
            with open(got_file, "w") as got_fp:
                got_fp.writelines(got)
                pass
            pass
        else:
            print("Yay! %s matches" % python_file)
        print('-' * 30)


def run_tests(func, test_dir, match_files=None):
    old_dir = os.getcwd()
    os.chdir(test_dir)
    for python_file in os.listdir(os.getcwd()):
        if python_file.endswith(".py"):
            if not match_files or python_file in match_files:
                compare_one(func, python_file)
                pass
            pass
        pass
    os.chdir(old_dir)
    return
