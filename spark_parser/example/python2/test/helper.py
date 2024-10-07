import difflib
import os
import sys


def helper_init(file, subdir):
    # I hate how clumsy Python is here
    dirname = os.path.join(".", os.path.dirname(file))
    parent_dir = os.path.join("..", os.path.dirname(file))
    sys.path.append(parent_dir)
    return os.path.join(dirname, subdir)


def compare_one(func, python_file, verbose=True):
    from spark_parser.example.python2.py2_scan import ENDMARKER

    right_file = python_file[:-2] + "right"
    got_file = python_file[:-2] + "got"
    # Python 2.5 tolerance
    py_fp = open(python_file, "r")
    input_data = py_fp.read() + ENDMARKER
    items = func(input_data)
    got = [str(t) + "\n" for t in items]
    same = True
    right_fp = open(right_file, "r")
    right_data = right_fp.readlines()
    lines = difflib.unified_diff(got, right_data, fromfile=right_file, tofile=got_file)
    for line in lines:
        same = False
        sys.stdout.write(line)
        pass
    if not same:
        got_fp = open(got_file, "w")
        got_fp.writelines(got)
        got_fp.close()
    else:
        if verbose:
            print("Yay! %s matches" % python_file)
        if verbose:
            print("-" * 30)
    py_fp.close()
    right_fp.close()
    return same


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


def run_tests_unit(cls, func, test_dir, match_files=None, verbose=False):
    old_dir = os.getcwd()
    os.chdir(test_dir)
    for python_file in os.listdir(os.getcwd()):
        if python_file.endswith(".py"):
            print(python_file)
            if not match_files or python_file in match_files:
                cls.assertTrue(compare_one(func, python_file, verbose), python_file)
                pass
            pass
        pass
    os.chdir(old_dir)
    return
