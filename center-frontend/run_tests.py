import sys

import glob2
import xmlrunner
import unittest

from os.path import join, realpath, pardir, dirname

# Add libtuto to python path
current_dir = dirname(realpath(__file__))
libtuto_path = join(current_dir, pardir, "tuto-file-handling")
sys.path.append(libtuto_path)

# Run test
test_files = glob2.glob('*tests/**/**_tests.py')
module_strings = [test_file[0:len(test_file)-3].replace('/', '.')
                  for test_file in test_files if "qt/" not in test_file]
suites = [unittest.defaultTestLoader.loadTestsFromName(
    test_file) for test_file in module_strings]
test_suite = unittest.TestSuite(suites)
test_runner = xmlrunner.XMLTestRunner(output='test-reports')

test_runner.run(test_suite)
