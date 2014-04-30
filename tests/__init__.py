#!/usr/bin/python
import functools
import optparse
import sys
# Install the Python unittest2 package before you run this script.
import unittest
import os

USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules"""

#: whether to skip tests which require authentication
SKIP_AUTH_TESTS = int(os.environ.get('SKIP_AUTH_TESTS', True))

skip_auth = functools.partial(
    unittest.skipIf, SKIP_AUTH_TESTS, 'Skipped test which needs authentication'
)


def main(sdk_path, test_path):
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest.loader.TestLoader().discover(test_path)

    # Uncomment to get logging during tests
    # logging.getLogger().setLevel(logging.DEBUG)

    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    if len(args) != 2:
        print 'Error: Exactly 2 arguments required.'
        parser.print_help()
        sys.exit(1)
    SDK_PATH = args[0]
    TEST_PATH = args[1]
    main(SDK_PATH, TEST_PATH)
