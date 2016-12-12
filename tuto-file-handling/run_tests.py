import unittest
import xmlrunner

import glob2

test_files = glob2.glob('*tests/**/**_tests.py')
module_strings = [test_file[0:len(test_file)-3].replace('/', '.')
                  for test_file in test_files]
suites = [unittest.defaultTestLoader.loadTestsFromName(
    test_file) for test_file in module_strings]
test_suite = unittest.TestSuite(suites)
test_runner = xmlrunner.XMLTestRunner(output='test-reports')

test_runner.run(test_suite)
